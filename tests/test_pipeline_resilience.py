from datetime import datetime, timezone

from research_agent.config import AppConfig
from research_agent.llm import LLMError
from research_agent.models import Candidate, QualityScore, RelevanceDecision
from research_agent.pipeline import generate_report, run_pipeline
from research_agent.state import load_state


def make_candidate(idx: int, title: str) -> Candidate:
    return Candidate(
        id=f"id-{idx}",
        source="arxiv",
        title=title,
        url=f"https://example.com/{idx}",
        published_at=datetime(2026, 6, idx, tzinfo=timezone.utc),
        abstract="abstract",
    )


def test_run_pipeline_skips_failed_report_and_tries_next_candidate(monkeypatch, tmp_path):
    first = make_candidate(1, "Top Paper")
    second = make_candidate(2, "Fallback Paper")
    config = AppConfig(
        openai_base_url="https://example.com/v1",
        openai_api_key="key",
        stage1_model="stage1",
        stage2_model="stage2",
        report_model="report",
        max_reports=1,
        send_email=False,
        state_path=tmp_path / "state.json",
        report_dir=tmp_path / "reports",
    )

    monkeypatch.setattr("research_agent.pipeline.collect_candidates", lambda cfg: [first, second])
    monkeypatch.setattr(
        "research_agent.pipeline.classify_relevance",
        lambda llm, cfg, candidate: RelevanceDecision(True, "AI Alignment", 10, "relevant"),
    )

    def fake_score(llm, cfg, candidate, relevance):
        overall = 10 if candidate.id == first.id else 9
        return QualityScore(overall, overall, overall, overall, overall, overall, "strong", "reason")

    monkeypatch.setattr("research_agent.pipeline.score_candidate", fake_score)
    monkeypatch.setattr("research_agent.pipeline.load_document_text", lambda session, candidate: ("document", "pdf"))

    attempted: list[str] = []

    def fake_generate_report(llm, cfg, candidate, document_text):
        attempted.append(candidate.id)
        if candidate.id == first.id:
            raise LLMError("503 Service Unavailable")
        return "## TL;DR\nfallback report"

    monkeypatch.setattr("research_agent.pipeline.generate_report", fake_generate_report)

    result = run_pipeline(config)

    assert attempted == [first.id, second.id]
    assert [report.candidate.id for report in result.digest.reports] == [second.id]

    state = load_state(config.state_path)
    assert first.id not in state.processed
    assert second.id in state.processed


def test_run_pipeline_emits_fallback_when_all_reports_fail(monkeypatch, tmp_path):
    first = make_candidate(1, "Top Paper")
    second = make_candidate(2, "Fallback Paper")
    config = AppConfig(
        openai_base_url="https://example.com/v1",
        openai_api_key="key",
        stage1_model="stage1",
        stage2_model="stage2",
        report_model="report",
        max_reports=1,
        send_email=False,
        state_path=tmp_path / "state.json",
        report_dir=tmp_path / "reports",
    )

    monkeypatch.setattr("research_agent.pipeline.collect_candidates", lambda cfg: [first, second])
    monkeypatch.setattr(
        "research_agent.pipeline.classify_relevance",
        lambda llm, cfg, candidate: RelevanceDecision(True, "AI Alignment", 10, "relevant"),
    )
    monkeypatch.setattr(
        "research_agent.pipeline.score_candidate",
        lambda llm, cfg, candidate, relevance: QualityScore(9, 9, 9, 9, 9, 9, "strong", "reason"),
    )
    monkeypatch.setattr("research_agent.pipeline.load_document_text", lambda session, candidate: ("document", "pdf"))
    monkeypatch.setattr(
        "research_agent.pipeline.generate_report",
        lambda llm, cfg, candidate, document_text: (_ for _ in ()).throw(LLMError("503 Service Unavailable")),
    )

    result = run_pipeline(config)

    assert len(result.digest.reports) == 1
    assert result.digest.report_failure_count == 2
    assert result.digest.reports[0].text_source == "report_generation_failed"
    assert "深度报告生成失败" in result.digest.reports[0].markdown

    state = load_state(config.state_path)
    assert first.id not in state.processed
    assert second.id not in state.processed


def test_generate_report_falls_back_to_short_context_and_fallback_model():
    candidate = make_candidate(1, "Top Paper")
    config = AppConfig(
        openai_base_url="https://example.com/v1",
        openai_api_key="key",
        report_model="report",
        report_fallback_model="fallback",
        report_max_chars=90,
        report_fallback_max_chars=25,
        report_max_retries=1,
    )

    class FakeLLM:
        def __init__(self):
            self.calls: list[tuple[str, int]] = []

        def chat(self, model, messages, temperature):
            user_text = messages[-1]["content"]
            self.calls.append((model, len(user_text)))
            if model == "fallback":
                return "## TL;DR\nfallback success"
            raise LLMError("503 Service Unavailable")

    llm = FakeLLM()

    markdown = generate_report(llm, config, candidate, "x" * 200)

    assert markdown.startswith("## TL;DR")
    assert [model for model, _ in llm.calls] == ["report", "report", "fallback"]
    assert llm.calls[1][1] < llm.calls[0][1]
    assert llm.calls[2][1] == llm.calls[1][1]


def test_run_pipeline_stops_report_attempts_after_consecutive_failures(monkeypatch, tmp_path):
    candidates = [make_candidate(idx, f"Paper {idx}") for idx in range(1, 6)]
    config = AppConfig(
        openai_base_url="https://example.com/v1",
        openai_api_key="key",
        stage1_model="stage1",
        stage2_model="stage2",
        report_model="report",
        max_reports=3,
        report_consecutive_failure_limit=2,
        send_email=False,
        state_path=tmp_path / "state.json",
        report_dir=tmp_path / "reports",
    )

    monkeypatch.setattr("research_agent.pipeline.collect_candidates", lambda cfg: candidates)
    monkeypatch.setattr(
        "research_agent.pipeline.classify_relevance",
        lambda llm, cfg, candidate: RelevanceDecision(True, "AI Alignment", 10, "relevant"),
    )
    monkeypatch.setattr(
        "research_agent.pipeline.score_candidate",
        lambda llm, cfg, candidate, relevance: QualityScore(9, 9, 9, 9, 9, 9, "strong", "reason"),
    )
    monkeypatch.setattr("research_agent.pipeline.load_document_text", lambda session, candidate: ("document", "pdf"))

    attempted: list[str] = []

    def fail_report(llm, cfg, candidate, document_text):
        attempted.append(candidate.id)
        raise LLMError("503 Service Unavailable")

    monkeypatch.setattr("research_agent.pipeline.generate_report", fail_report)

    result = run_pipeline(config)

    assert attempted == ["id-5", "id-4"]
    assert result.digest.report_failure_count == 2
    assert len(result.digest.reports) == 2
    assert all(report.text_source == "report_generation_failed" for report in result.digest.reports)
