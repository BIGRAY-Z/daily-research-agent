from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from research_agent.collectors import ArxivCollector, HuggingFacePapersCollector, default_web_collectors
from research_agent.config import AppConfig
from research_agent.delivery.email import send_email
from research_agent.http import build_session, get_with_retries
from research_agent.llm import LLMClient
from research_agent.models import Candidate, DailyDigest, DeepReport, QualityScore, RelevanceDecision
from research_agent.pdf import fetch_pdf_text
from research_agent.prompts import (
    REPORT_SYSTEM_PROMPT,
    STAGE1_SYSTEM_PROMPT,
    STAGE2_SYSTEM_PROMPT,
    report_user_prompt,
    stage1_user_prompt,
    stage2_user_prompt,
)
from research_agent.render import render_digest_markdown, write_digest_artifacts, write_pdf_from_html
from research_agent.state import candidate_seen, load_state, mark_candidate_seen, save_state
from research_agent.text import clean_text, truncate_text

from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


def select_top_candidates(
    ranked: list[tuple[Candidate, QualityScore]],
    max_reports: int,
) -> list[tuple[Candidate, QualityScore]]:
    return sorted(
        ranked,
        key=lambda item: (item[1].overall, item[1].relevance, item[0].recency_key()),
        reverse=True,
    )[:max_reports]


@dataclass(slots=True)
class RunResult:
    digest: DailyDigest
    markdown_path: Path
    json_path: Path
    html_path: Path
    pdf_path: Path | None
    email_sent: bool


def collect_candidates(config: AppConfig) -> list[Candidate]:
    if config.skip_sources:
        return []

    session = build_session()
    collectors = [
        ArxivCollector(session),
        HuggingFacePapersCollector(session),
        *default_web_collectors(
            session,
            alignment_urls=config.alignment_forum_urls,
            anthropic_urls=config.anthropic_urls,
            circuits_urls=config.transformer_circuits_urls,
        ),
    ]

    candidates: dict[str, Candidate] = {}
    for collector in collectors:
        try:
            for candidate in collector.collect(config.lookback_days):
                if candidate.id not in candidates:
                    candidates[candidate.id] = candidate
        except Exception as exc:
            LOGGER.warning("Collector %s failed: %s", getattr(collector, "source_name", collector), exc)
    return list(candidates.values())


def run_pipeline(config: AppConfig, *, dry_run: bool = False, skip_llm: bool = False) -> RunResult:
    if not skip_llm:
        config.validate_llm()
    if config.send_email and not dry_run:
        config.validate_email()

    now = datetime.now(timezone.utc)
    run_date = artifact_run_id(now, dry_run)
    LOGGER.info("Starting run for %s; dry_run=%s skip_llm=%s", run_date, dry_run, skip_llm)
    state = load_state(config.state_path)
    candidates = collect_candidates(config)
    fresh_candidates = [candidate for candidate in candidates if not candidate_seen(state, candidate)]
    already_processed_count = len(candidates) - len(fresh_candidates)
    LOGGER.info("Collected %d candidates; %d are fresh", len(candidates), len(fresh_candidates))

    if skip_llm:
        digest = _build_collect_only_digest(run_date, fresh_candidates, already_processed_count)
        markdown_path, json_path, html_path = write_digest_artifacts(config.report_dir, digest)
        pdf_path = make_pdf_artifact(html_path)
        return RunResult(digest=digest, markdown_path=markdown_path, json_path=json_path, html_path=html_path, pdf_path=pdf_path, email_sent=False)

    llm = LLMClient(
        config.openai_base_url,
        config.openai_api_key,
        timeout_seconds=config.llm_timeout_seconds,
    )
    relevant: list[tuple[Candidate, RelevanceDecision]] = []
    stage1_filtered_count = 0
    stage2_filtered_count = 0
    report_failure_count = 0
    for index, candidate in enumerate(fresh_candidates, start=1):
        LOGGER.info("Stage 1 relevance %d/%d: %s", index, len(fresh_candidates), candidate.title)
        decision = classify_relevance(llm, config, candidate)
        if decision.relevant and decision.confidence >= config.stage1_confidence_threshold:
            relevant.append((candidate, decision))
        else:
            stage1_filtered_count += 1
    LOGGER.info("Stage 1 kept %d candidates", len(relevant))

    scored: list[tuple[Candidate, RelevanceDecision, QualityScore]] = []
    for index, (candidate, decision) in enumerate(relevant, start=1):
        LOGGER.info("Stage 2 scoring %d/%d: %s", index, len(relevant), candidate.title)
        score = score_candidate(llm, config, candidate, decision)
        if score.priority != "skip":
            scored.append((candidate, decision, score))
        else:
            stage2_filtered_count += 1

    ranked = select_top_candidates([(candidate, score) for candidate, _, score in scored], len(scored))
    LOGGER.info("Selected up to %d reports from %d scored candidates", config.max_reports, len(scored))
    decision_by_id = {candidate.id: decision for candidate, decision, _ in scored}
    reports: list[DeepReport] = []
    failed_reports: list[tuple[Candidate, RelevanceDecision, QualityScore, str]] = []
    session = build_session()
    for index, (candidate, score) in enumerate(ranked, start=1):
        if len(reports) >= config.max_reports:
            break
        LOGGER.info("Generating report %d/%d: %s", index, len(ranked), candidate.title)
        decision = decision_by_id[candidate.id]
        try:
            document_text, text_source = load_document_text(session, candidate)
            markdown = generate_report(llm, config, candidate, document_text)
        except Exception as exc:
            report_failure_count += 1
            failed_reports.append((candidate, decision, score, str(exc)))
            LOGGER.warning("Report generation failed for %s; trying next candidate: %s", candidate.title, exc)
            continue
        reports.append(
            DeepReport(
                candidate=candidate,
                relevance=decision,
                score=score,
                markdown=markdown,
                text_source=text_source,
            )
        )
        if not dry_run:
            mark_candidate_seen(state, candidate, now.isoformat())

    if not reports and failed_reports:
        LOGGER.warning("All report-generation attempts failed; emitting fallback candidate summaries")
        for candidate, decision, score, error in failed_reports[: config.max_reports]:
            reports.append(build_report_failure_fallback(candidate, decision, score, error))

    skipped_count = already_processed_count + stage1_filtered_count + stage2_filtered_count + report_failure_count
    digest = DailyDigest(
        run_date=run_date,
        reports=reports,
        skipped_count=skipped_count,
        candidate_count=len(candidates),
        already_processed_count=already_processed_count,
        stage1_filtered_count=stage1_filtered_count,
        stage2_filtered_count=stage2_filtered_count,
        report_failure_count=report_failure_count,
    )
    markdown_path, json_path, html_path = write_digest_artifacts(config.report_dir, digest)
    pdf_path = make_pdf_artifact(html_path)
    if not dry_run:
        save_state(config.state_path, state)

    email_sent = False
    if config.send_email and not dry_run:
        body = render_digest_markdown(digest)
        send_email(
            smtp=config.smtp_config(),
            subject=f"AI Safety Research Daily - {run_date}",
            body_markdown=body,
            sender=config.email_from,
            recipients=config.email_to,
            attachments=[path for path in [pdf_path, html_path, json_path] if path is not None],
        )
        email_sent = True

    return RunResult(digest=digest, markdown_path=markdown_path, json_path=json_path, html_path=html_path, pdf_path=pdf_path, email_sent=email_sent)


def classify_relevance(llm: LLMClient, config: AppConfig, candidate: Candidate) -> RelevanceDecision:
    raw = llm.chat_json(config.stage1_model, STAGE1_SYSTEM_PROMPT, stage1_user_prompt(candidate))
    return RelevanceDecision(
        relevant=bool(raw.get("relevant", False)),
        domain=str(raw.get("domain", "Adjacent")),
        confidence=int(raw.get("confidence", 0)),
        reason=str(raw.get("reason", "")),
    )


def score_candidate(
    llm: LLMClient,
    config: AppConfig,
    candidate: Candidate,
    relevance: RelevanceDecision,
) -> QualityScore:
    raw = llm.chat_json(config.stage2_model, STAGE2_SYSTEM_PROMPT, stage2_user_prompt(candidate, relevance))
    return QualityScore(
        relevance=float(raw.get("relevance", 0)),
        novelty=float(raw.get("novelty", 0)),
        technical_depth=float(raw.get("technical_depth", 0)),
        research_value=float(raw.get("research_value", 0)),
        credibility=float(raw.get("credibility", 0)),
        overall=float(raw.get("overall", 0)),
        priority=str(raw.get("priority", "maybe")),
        reason=str(raw.get("reason", "")),
    )


def load_document_text(session, candidate: Candidate) -> tuple[str, str]:
    if candidate.pdf_url:
        try:
            text = fetch_pdf_text(session, candidate.pdf_url)
            if text:
                return text, "pdf"
        except Exception as exc:
            LOGGER.warning("PDF extraction failed for %s: %s", candidate.url, exc)
    if candidate.url.startswith("http"):
        try:
            response = get_with_retries(session, candidate.url, timeout=30, max_retries=1)
            text = extract_article_text(response.text)
            if len(text) > len(clean_text(candidate.body_text or candidate.abstract)):
                return text, "html"
        except Exception as exc:
            LOGGER.warning("HTML article extraction failed for %s: %s", candidate.url, exc)
    fallback = clean_text(candidate.body_text or candidate.abstract)
    return fallback, "abstract_or_html"


def extract_article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "nav", "footer", "header"]):
        node.decompose()
    main = soup.find("article") or soup.find("main") or soup.body or soup
    paragraphs = [clean_text(item.get_text(" ")) for item in main.find_all(["h1", "h2", "h3", "p", "li"])]
    text = "\n".join(item for item in paragraphs if len(item) > 20)
    return clean_text(text)


def generate_report(llm: LLMClient, config: AppConfig, candidate: Candidate, document_text: str) -> str:
    report_llm = LLMClient(
        config.openai_base_url,
        config.openai_api_key,
        timeout_seconds=config.report_timeout_seconds,
    )
    prepared_text = prepare_report_text(document_text, config.report_max_chars)
    LOGGER.info(
        "Report input for %s: %d chars truncated to %d chars; timeout=%ss",
        candidate.title,
        len(document_text),
        len(prepared_text),
        config.report_timeout_seconds,
    )
    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": report_user_prompt(candidate, prepared_text)},
    ]
    return report_llm.chat(config.report_model, messages, temperature=0.2)


def prepare_report_text(document_text: str, max_chars: int) -> str:
    return truncate_text(document_text, max_chars)


def make_pdf_artifact(html_path: Path) -> Path | None:
    pdf_path = html_path.with_suffix(".pdf")
    try:
        write_pdf_from_html(html_path, pdf_path)
        return pdf_path
    except Exception as exc:
        LOGGER.warning("PDF generation failed for %s: %s", html_path, exc)
        return None


def build_report_failure_fallback(
    candidate: Candidate,
    decision: RelevanceDecision,
    score: QualityScore,
    error: str,
) -> DeepReport:
    markdown = f"""## 深度报告生成失败

这篇文章通过了粗筛和质量评分，但报告模型或中转站在生成长报告时失败。本条目保留为候选摘要，失败文章不会写入已处理状态，后续自动运行仍会重试。

- 失败原因: {clean_text(error)}
- 候选摘要: {candidate.abstract or candidate.body_text or "No abstract extracted."}
"""
    return DeepReport(
        candidate=candidate,
        relevance=decision,
        score=score,
        markdown=markdown,
        text_source="report_generation_failed",
    )


def artifact_run_id(now: datetime, dry_run: bool) -> str:
    if dry_run:
        return f"dry-run-{now.strftime('%Y-%m-%d-%H%M%S')}"
    return now.date().isoformat()


def update_state_after_reports(
    config: AppConfig,
    digest: DailyDigest,
    candidates: list[Candidate],
    timestamp: str,
    *,
    dry_run: bool,
):
    state = load_state(config.state_path)
    if dry_run:
        return state
    reported_ids = {report.candidate.id for report in digest.reports}
    for candidate in candidates:
        if candidate.id in reported_ids:
            mark_candidate_seen(state, candidate, timestamp)
    save_state(config.state_path, state)
    return state


def _build_collect_only_digest(run_date: str, candidates: list[Candidate], skipped_count: int) -> DailyDigest:
    reports: list[DeepReport] = []
    for candidate in candidates[:10]:
        reports.append(
            DeepReport(
                candidate=candidate,
                relevance=RelevanceDecision(True, "Unclassified", 0, "LLM skipped"),
                score=QualityScore(0, 0, 0, 0, 0, 0, "maybe", "LLM skipped"),
                markdown=f"## 摘要\n{candidate.abstract or candidate.body_text or 'No abstract extracted.'}",
                text_source="metadata",
            )
        )
    return DailyDigest(
        run_date=run_date,
        reports=reports,
        skipped_count=skipped_count,
        candidate_count=len(candidates),
        already_processed_count=skipped_count,
    )
