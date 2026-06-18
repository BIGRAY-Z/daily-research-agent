from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

import markdown as markdown_lib

from research_agent.models import DailyDigest, DeepReport, dataclass_to_jsonable
from research_agent.text import slugify


def render_digest_markdown(digest: DailyDigest) -> str:
    lines = [
        f"# AI Safety Research Daily - {digest.run_date}",
        "",
        f"- Selected reports: {len(digest.reports)}",
        f"- Skipped or already processed: {digest.skipped_count}",
    ]
    if digest.candidate_count:
        lines.append(f"- Raw candidates: {digest.candidate_count}")
    if any(
        [
            digest.already_processed_count,
            digest.stage1_filtered_count,
            digest.stage2_filtered_count,
            digest.stage1_failure_count,
            digest.stage2_failure_count,
            digest.report_failure_count,
        ]
    ):
        lines.extend(
            [
                f"- Already processed: {digest.already_processed_count}",
                f"- Stage 1 filtered: {digest.stage1_filtered_count}",
                f"- Stage 2 filtered: {digest.stage2_filtered_count}",
                f"- Stage 1 LLM failed: {digest.stage1_failure_count}",
                f"- Stage 2 LLM failed: {digest.stage2_failure_count}",
                f"- Report generation failed: {digest.report_failure_count}",
            ]
        )
    lines.append("")

    if not digest.reports:
        lines.append("今天没有筛选出新的高优先级文章。")
        return "\n".join(lines).strip() + "\n"

    lines.append("## Top Items")
    for index, report in enumerate(digest.reports, start=1):
        candidate = report.candidate
        lines.extend(
            [
                "",
                f"### {index}. {candidate.title}",
                "",
                f"- Source: {candidate.source}",
                f"- URL: {candidate.url}",
                f"- Domain: {report.relevance.domain} ({report.relevance.confidence}/10)",
                f"- Overall: {format_score(report.score.overall)}",
                f"- Priority: {report.score.priority}",
                f"- Text source: {report.text_source}",
                f"- Score reason: {report.score.reason}",
                "",
                report.markdown.strip(),
            ]
        )
    return "\n".join(lines).strip() + "\n"


def render_digest_html(digest: DailyDigest) -> str:
    cards = []
    for index, report in enumerate(digest.reports, start=1):
        candidate = report.candidate
        report_body = markdown_to_basic_html(report.markdown)
        cards.append(
            f"""
            <article class="report-card">
              <header class="report-header">
                <div class="rank">#{index}</div>
                <div>
                  <h2>{escape(candidate.title)}</h2>
                  <a href="{escape(candidate.url)}">{escape(candidate.url)}</a>
                </div>
                <div class="score-badge">{format_score(report.score.overall)}</div>
              </header>
              <div class="meta-grid">
                <div><span>来源</span><strong>{escape(candidate.source)}</strong></div>
                <div><span>领域</span><strong>{escape(report.relevance.domain)} ({report.relevance.confidence}/10)</strong></div>
                <div><span>优先级</span><strong>{escape(report.score.priority)}</strong></div>
                <div><span>文本来源</span><strong>{escape(report.text_source)}</strong></div>
              </div>
              <section class="score-reason">
                <h3>评分理由</h3>
                <p>{escape(report.score.reason)}</p>
              </section>
              <section class="report-body">{report_body}</section>
            </article>
            """
        )

    if not cards:
        cards.append('<article class="report-card"><p>今天没有筛选出新的高优先级文章。</p></article>')

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Safety Research Daily - {escape(digest.run_date)}</title>
  <script>
    window.MathJax = {{
      tex: {{ inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] }},
      svg: {{ fontCache: 'global' }}
    }};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --paper: #ffffff;
      --ink: #18202a;
      --muted: #667085;
      --line: #d8dee8;
      --accent: #0b6bcb;
      --accent-2: #0f766e;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    .topbar {{
      display: flex;
      gap: 20px;
      justify-content: space-between;
      align-items: end;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.15;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 10px;
      min-width: min(420px, 100%);
    }}
    .summary div, .meta-grid div {{
      border: 1px solid var(--line);
      background: #fbfcfe;
      padding: 10px 12px;
      border-radius: 8px;
    }}
    span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .report-card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
      margin: 18px 0;
      box-shadow: 0 8px 20px rgba(24, 32, 42, 0.05);
    }}
    .report-header {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 14px;
      align-items: start;
    }}
    .rank {{
      color: var(--accent);
      font-weight: 700;
      font-size: 20px;
    }}
    h2 {{
      margin: 0 0 4px;
      font-size: 22px;
      line-height: 1.28;
    }}
    h3 {{
      margin-top: 24px;
      border-top: 1px solid var(--line);
      padding-top: 16px;
    }}
    a {{ color: var(--accent); word-break: break-word; }}
    .score-badge {{
      min-width: 54px;
      height: 54px;
      border-radius: 50%;
      background: var(--accent-2);
      color: white;
      display: grid;
      place-items: center;
      font-size: 22px;
      font-weight: 700;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
      margin: 18px 0;
    }}
    .score-reason {{
      background: #f8fafc;
      border-left: 4px solid var(--accent);
      padding: 1px 14px 12px;
      margin-bottom: 18px;
    }}
    .report-body h1 {{ font-size: 28px; margin-top: 28px; }}
    .report-body h2 {{ font-size: 22px; margin-top: 26px; }}
    .report-body p {{ margin: 10px 0; }}
    .report-body li {{ margin: 6px 0; }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
    }}
    @media (max-width: 760px) {{
      .topbar, .report-header, .summary, .meta-grid {{
        display: block;
      }}
      .summary div, .meta-grid div {{ margin: 8px 0; }}
      .score-badge {{ margin-top: 12px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="topbar">
      <div>
        <h1>AI Safety Research Daily</h1>
        <div>{escape(digest.run_date)} 中文研究日报</div>
      </div>
      <div class="summary">
        <div><span>精选报告</span><strong>{len(digest.reports)}</strong></div>
        <div><span>跳过/已处理</span><strong>{digest.skipped_count}</strong></div>
        <div><span>原始候选</span><strong>{digest.candidate_count}</strong></div>
        <div><span>已处理</span><strong>{digest.already_processed_count}</strong></div>
        <div><span>粗筛过滤</span><strong>{digest.stage1_filtered_count}</strong></div>
        <div><span>质量过滤</span><strong>{digest.stage2_filtered_count}</strong></div>
        <div><span>粗筛失败</span><strong>{digest.stage1_failure_count}</strong></div>
        <div><span>质量失败</span><strong>{digest.stage2_failure_count}</strong></div>
        <div><span>报告失败</span><strong>{digest.report_failure_count}</strong></div>
      </div>
    </section>
    {''.join(cards)}
  </main>
</body>
</html>
"""


def markdown_to_basic_html(markdown: str) -> str:
    protected, math_map = protect_math(markdown)
    html = markdown_lib.markdown(
        protected,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    for token, rendered in math_map.items():
        html = html.replace(token, rendered)
    return html


def protect_math(markdown: str) -> tuple[str, dict[str, str]]:
    math_map: dict[str, str] = {}

    def replace_display(match: re.Match[str]) -> str:
        token = f"MATHDISPLAY{len(math_map)}TOKEN"
        math_map[token] = f'<div class="math-display">\\[{escape(match.group(1))}\\]</div>'
        return token

    def replace_inline(match: re.Match[str]) -> str:
        token = f"MATHINLINE{len(math_map)}TOKEN"
        math_map[token] = f'<span class="math">\\({escape(match.group(1))}\\)</span>'
        return token

    text = re.sub(r"\$\$(.+?)\$\$", replace_display, markdown, flags=re.DOTALL)
    text = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", replace_inline, text, flags=re.DOTALL)
    return text, math_map


def format_score(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def write_digest_artifacts(report_dir: str | Path, digest: DailyDigest) -> tuple[Path, Path, Path]:
    root = Path(report_dir) / digest.run_date
    items_dir = root / "items"
    items_dir.mkdir(parents=True, exist_ok=True)

    for index, report in enumerate(digest.reports, start=1):
        item_path = items_dir / f"{index:02d}-{slugify(report.candidate.title)}.md"
        item_path.write_text(report.markdown.strip() + "\n", encoding="utf-8")

    markdown_path = root / "digest.md"
    json_path = root / "digest.json"
    html_path = root / "digest.html"
    markdown_path.write_text(render_digest_markdown(digest), encoding="utf-8")
    html_path.write_text(render_digest_html(digest), encoding="utf-8")
    json_path.write_text(
        json.dumps(dataclass_to_jsonable(digest), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return markdown_path, json_path, html_path


def write_pdf_from_html(html_path: Path, pdf_path: Path) -> None:
    from bs4 import BeautifulSoup
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    register_cjk_font()
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "CJKBody",
        parent=styles["BodyText"],
        fontName="CJK",
        fontSize=10.5,
        leading=15,
        spaceAfter=7,
    )
    heading1 = ParagraphStyle("CJKH1", parent=base, fontSize=18, leading=23, spaceBefore=12, spaceAfter=10)
    heading2 = ParagraphStyle("CJKH2", parent=base, fontSize=15, leading=20, spaceBefore=10, spaceAfter=8)
    heading3 = ParagraphStyle("CJKH3", parent=base, fontSize=13, leading=18, spaceBefore=8, spaceAfter=6)
    small = ParagraphStyle("CJKSmall", parent=base, fontSize=9, leading=13, textColor="#4b5563")

    story = []
    for node in (soup.body or soup).find_all(["h1", "h2", "h3", "p", "li", "hr"], recursive=True):
        if node.name == "hr":
            story.append(PageBreak())
            continue
        text = clean_pdf_text(node.get_text(" ", strip=True))
        if not text:
            continue
        style = {"h1": heading1, "h2": heading2, "h3": heading3, "li": base, "p": base}.get(node.name, base)
        if node.name == "li":
            text = f"• {text}"
        if len(text) < 80 and node.find_parent(class_="meta-grid"):
            style = small
        story.append(Paragraph(escape_for_reportlab(text), style))
        story.append(Spacer(1, 0.12 * cm))

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title=html_path.stem,
    )
    doc.build(story)


def register_cjk_font() -> None:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if "CJK" in pdfmetrics.getRegisteredFontNames():
        return
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for font_path in candidates:
        path = Path(font_path)
        if path.exists():
            pdfmetrics.registerFont(TTFont("CJK", str(path)))
            return
    raise RuntimeError("No usable TTF/TTC font found for PDF generation")


def clean_pdf_text(text: str) -> str:
    return text.replace("\u200b", "").strip()


def escape_for_reportlab(text: str) -> str:
    return escape(text).replace("\n", "<br/>")
