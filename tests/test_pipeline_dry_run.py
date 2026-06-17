from datetime import datetime, timezone

from research_agent.config import AppConfig
from research_agent.models import Candidate, DailyDigest
from research_agent.pipeline import artifact_run_id, extract_article_text, update_state_after_reports
from research_agent.state import candidate_seen


def test_dry_run_artifact_run_id_does_not_use_plain_date():
    now = datetime(2026, 6, 17, 5, 1, 2, tzinfo=timezone.utc)
    assert artifact_run_id(now, dry_run=True).startswith("dry-run-2026-06-17-050102")
    assert artifact_run_id(now, dry_run=False) == "2026-06-17"


def test_dry_run_does_not_mark_state():
    candidate = Candidate(
        id="arxiv:1234",
        source="arxiv",
        title="paper",
        url="https://example.com",
        published_at=None,
        abstract="abstract",
    )
    digest = DailyDigest(run_date="dry-run-2026-06-17-050102", reports=[], skipped_count=0)
    config = AppConfig()
    state = update_state_after_reports(config, digest, [candidate], "2026-06-17T05:01:02+00:00", dry_run=True)
    assert not candidate_seen(state, candidate)


def test_extract_article_text_prefers_article_body():
    html = """
    <html><body>
      <nav>Navigation should be ignored completely</nav>
      <article>
        <h1>Natural Language Autoencoders</h1>
        <p>This paragraph contains the actual interpretability article body.</p>
        <p>Another paragraph explains the method and experiments in detail.</p>
      </article>
    </body></html>
    """
    text = extract_article_text(html)
    assert "actual interpretability article body" in text
    assert "method and experiments" in text
    assert "Navigation" not in text
