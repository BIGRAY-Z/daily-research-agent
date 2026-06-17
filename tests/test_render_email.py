from datetime import datetime, timezone

from research_agent.delivery.email import build_email_message
from research_agent.models import Candidate, DailyDigest, DeepReport, QualityScore, RelevanceDecision
from research_agent.render import markdown_to_basic_html, render_digest_html, render_digest_markdown, write_pdf_from_html


def test_render_digest_contains_title_and_score():
    candidate = Candidate(
        id="id-1",
        source="arxiv",
        title="A Good MI Paper",
        url="https://example.com/paper",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="abstract",
    )
    report = DeepReport(
        candidate=candidate,
        relevance=RelevanceDecision(True, "Mechanistic Interpretability", 9, "relevant"),
        score=QualityScore(9, 8, 9, 9, 8, 9, "must_read", "strong"),
        markdown="## TL;DR\nUseful paper.",
        text_source="pdf",
    )
    digest = DailyDigest(run_date="2026-06-16", reports=[report], skipped_count=2)
    markdown = render_digest_markdown(digest)
    assert "A Good MI Paper" in markdown
    assert "Overall: 9" in markdown


def test_render_digest_html_contains_visual_sections():
    candidate = Candidate(
        id="id-1",
        source="arxiv",
        title="A Good MI Paper",
        url="https://example.com/paper",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="abstract",
    )
    report = DeepReport(
        candidate=candidate,
        relevance=RelevanceDecision(True, "Mechanistic Interpretability", 9, "relevant"),
        score=QualityScore(9, 8, 9, 9, 8, 9, "must_read", "strong"),
        markdown="## TL;DR\nUseful paper.",
        text_source="pdf",
    )
    digest = DailyDigest(run_date="2026-06-16", reports=[report], skipped_count=2)
    html = render_digest_html(digest)
    assert "<html" in html
    assert "A Good MI Paper" in html
    assert "score-badge" in html


def test_markdown_to_html_compiles_markdown_and_preserves_math():
    html = markdown_to_basic_html("## 标题\n\n- **重点**: $a^2+b^2=c^2$")
    assert "<h2>" in html
    assert "<ul>" in html
    assert "<strong>重点</strong>" in html
    assert '<span class="math">\\(a^2+b^2=c^2\\)</span>' in html


def test_build_email_message_sets_headers():
    msg = build_email_message(
        subject="Daily Report",
        body_markdown="# Report",
        sender="from@example.com",
        recipients=["to@example.com"],
    )
    assert msg["Subject"] == "Daily Report"
    assert msg["From"] == "from@example.com"
    assert msg["To"] == "to@example.com"


def test_build_email_message_plain_text_uses_utf8_charset():
    msg = build_email_message(
        subject="Daily Report",
        body_markdown="高度贴合 Alignment",
        sender="from@example.com",
        recipients=["to@example.com"],
    )
    assert msg.get_content_charset() == "utf-8"
    assert msg.get_content() == "高度贴合 Alignment\n"


def test_build_email_message_attaches_pdf_with_application_pdf(tmp_path):
    pdf_path = tmp_path / "digest.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    msg = build_email_message(
        subject="Daily Report",
        body_markdown="# Report",
        sender="from@example.com",
        recipients=["to@example.com"],
        attachments=[pdf_path],
    )
    attachment = list(msg.iter_attachments())[0]
    assert attachment.get_content_type() == "application/pdf"


def test_write_pdf_from_html_creates_pdf(tmp_path):
    html_path = tmp_path / "digest.html"
    pdf_path = tmp_path / "digest.pdf"
    html_path.write_text("<html><body><h1>中文报告</h1><p>hello</p></body></html>", encoding="utf-8")
    write_pdf_from_html(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.read_bytes().startswith(b"%PDF")
