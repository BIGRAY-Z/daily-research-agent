# Daily Research Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Python agent that collects recent AI safety research, filters and ranks it with OpenAI-compatible LLM APIs, generates deep reports, and sends a daily SMTP email from GitHub Actions.

**Architecture:** The project is a Python CLI package under `src/research_agent`. Collectors normalize source-specific data into shared `Candidate` objects; the pipeline deduplicates, filters, scores, reports, renders, delivers, and persists state. External systems are isolated behind `LLMClient`, source collectors, and delivery adapters so they can be mocked in tests.

**Tech Stack:** Python 3.11+, `requests`, `beautifulsoup4`, `pypdf`, `pytest`, GitHub Actions, OpenAI-compatible `/chat/completions`, SMTP over TLS/SSL.

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, pytest configuration.
- Create `.env.example`: all required and optional environment variables.
- Create `.github/workflows/daily-research-agent.yml`: daily and manual GitHub Actions workflow.
- Create `src/research_agent/__init__.py`: package version.
- Create `src/research_agent/__main__.py`: CLI entrypoint with `run`, `collect`, and `test-email`.
- Create `src/research_agent/config.py`: environment and CLI configuration.
- Create `src/research_agent/models.py`: dataclasses for candidates, scores, reports, state.
- Create `src/research_agent/state.py`: JSON state loading and saving.
- Create `src/research_agent/text.py`: text cleanup, slugging, JSON extraction helpers.
- Create `src/research_agent/http.py`: shared HTTP session with retries.
- Create `src/research_agent/collectors/__init__.py`: collector exports.
- Create `src/research_agent/collectors/base.py`: collector protocol and helpers.
- Create `src/research_agent/collectors/arxiv.py`: arXiv Atom collector.
- Create `src/research_agent/collectors/huggingface.py`: Hugging Face Papers collector.
- Create `src/research_agent/collectors/web_pages.py`: Alignment Forum, Anthropic, and Transformer Circuits page collectors.
- Create `src/research_agent/llm.py`: OpenAI-compatible chat client and JSON retry helpers.
- Create `src/research_agent/prompts.py`: stage 1, stage 2, and report prompts.
- Create `src/research_agent/pdf.py`: PDF download and text extraction.
- Create `src/research_agent/render.py`: Markdown and JSON report rendering.
- Create `src/research_agent/delivery/__init__.py`: delivery exports.
- Create `src/research_agent/delivery/email.py`: SMTP digest sender.
- Create `src/research_agent/delivery/notion.py`: reserved adapter with actionable error.
- Create `src/research_agent/pipeline.py`: orchestration.
- Create `tests/test_text.py`: JSON extraction, slugging, cleanup tests.
- Create `tests/test_state.py`: state load/save/dedup tests.
- Create `tests/test_ranking.py`: top-six ranking tests.
- Create `tests/test_render_email.py`: digest and SMTP message construction tests.
- Create `README_AGENT.md`: complete local, GitHub Actions, SMTP, and Notion instructions.

## Tasks

### Task 1: Project Skeleton and Shared Models

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/research_agent/__init__.py`
- Create: `src/research_agent/models.py`
- Create: `src/research_agent/text.py`
- Test: `tests/test_text.py`

- [ ] **Step 1: Write failing tests for text helpers**

```python
from research_agent.text import extract_json_object, slugify, clean_text


def test_extract_json_object_from_fenced_block():
    raw = '```json\n{"relevant": true, "confidence": 8}\n```'
    assert extract_json_object(raw)["confidence"] == 8


def test_extract_json_object_from_surrounding_text():
    raw = 'Here is the result: {"overall": 9, "priority": "must_read"} thanks'
    assert extract_json_object(raw)["priority"] == "must_read"


def test_slugify_keeps_readable_ascii():
    assert slugify("Sparse Autoencoders: Why / When?") == "sparse-autoencoders-why-when"


def test_clean_text_collapses_whitespace():
    assert clean_text(" A\\n\\n  B\\tC ") == "A B C"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_text.py -v`

Expected: FAIL because `research_agent.text` does not exist yet.

- [ ] **Step 3: Create package metadata and model/text helpers**

Create `pyproject.toml`, `.env.example`, `src/research_agent/__init__.py`, `src/research_agent/models.py`, and `src/research_agent/text.py` with dataclasses and helper functions used by later tasks.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_text.py -v`

Expected: PASS.

### Task 2: State Management

**Files:**
- Create: `src/research_agent/state.py`
- Test: `tests/test_state.py`

- [ ] **Step 1: Write failing state tests**

```python
from datetime import datetime, timezone

from research_agent.models import Candidate
from research_agent.state import load_state, save_state, candidate_seen, mark_candidate_seen


def make_candidate():
    return Candidate(
        id="arxiv:2606.00001",
        source="arxiv",
        title="Mechanistic Interpretability Test",
        url="https://arxiv.org/abs/2606.00001",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="test",
    )


def test_state_round_trip(tmp_path):
    path = tmp_path / "state.json"
    state = load_state(path)
    candidate = make_candidate()
    mark_candidate_seen(state, candidate, "2026-06-16T00:00:00+00:00")
    save_state(path, state)
    loaded = load_state(path)
    assert candidate_seen(loaded, candidate)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_state.py -v`

Expected: FAIL because `research_agent.state` does not exist yet.

- [ ] **Step 3: Implement JSON state loading, saving, and deduplication**

State stores processed candidate IDs in a JSON object with a `processed` mapping. Missing files return an empty state.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_state.py -v`

Expected: PASS.

### Task 3: LLM, Ranking, and Prompt Contracts

**Files:**
- Create: `src/research_agent/llm.py`
- Create: `src/research_agent/prompts.py`
- Modify: `src/research_agent/pipeline.py`
- Test: `tests/test_ranking.py`

- [ ] **Step 1: Write failing ranking tests**

```python
from datetime import datetime, timezone

from research_agent.models import Candidate, QualityScore
from research_agent.pipeline import select_top_candidates


def candidate(idx, score):
    return (
        Candidate(
            id=f"id-{idx}",
            source="test",
            title=f"paper {idx}",
            url=f"https://example.com/{idx}",
            published_at=datetime(2026, 6, idx, tzinfo=timezone.utc),
            abstract="abstract",
        ),
        QualityScore(
            relevance=score,
            novelty=score,
            technical_depth=score,
            research_value=score,
            credibility=score,
            overall=score,
            priority="strong",
            reason="reason",
        ),
    )


def test_select_top_candidates_limits_and_sorts():
    ranked = [candidate(i, float(i)) for i in range(1, 9)]
    selected = select_top_candidates(ranked, max_reports=6)
    assert [item[0].id for item in selected] == ["id-8", "id-7", "id-6", "id-5", "id-4", "id-3"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ranking.py -v`

Expected: FAIL because `research_agent.pipeline` does not exist yet.

- [ ] **Step 3: Implement LLM client, prompts, and ranking helper**

Implement a requests-based OpenAI-compatible client for `/chat/completions`, strict JSON extraction, retry on malformed JSON, and a pure `select_top_candidates` helper.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ranking.py -v`

Expected: PASS.

### Task 4: Collectors and PDF Extraction

**Files:**
- Create: `src/research_agent/http.py`
- Create: `src/research_agent/collectors/__init__.py`
- Create: `src/research_agent/collectors/base.py`
- Create: `src/research_agent/collectors/arxiv.py`
- Create: `src/research_agent/collectors/huggingface.py`
- Create: `src/research_agent/collectors/web_pages.py`
- Create: `src/research_agent/pdf.py`

- [ ] **Step 1: Implement shared HTTP and collector protocol**

Create a retrying `requests.Session`, a `Collector` protocol, and helpers for parsing dates and building stable IDs.

- [ ] **Step 2: Implement arXiv collector**

Use `https://export.arxiv.org/api/query`, topic queries, date filtering, Atom XML parsing, and PDF URL extraction.

- [ ] **Step 3: Implement Hugging Face Papers collector**

Fetch `https://huggingface.co/papers`, parse linked paper rows/cards, and extract title, URL, summary, and arXiv/PDF links when present.

- [ ] **Step 4: Implement Alignment Forum, Anthropic, and Transformer Circuits page collectors**

Use conservative HTML parsing for public pages and source-specific default URL lists. Failures return an empty list and a warning rather than crashing the whole run.

- [ ] **Step 5: Implement PDF utilities**

Download PDFs with size/time limits, extract text with `pypdf`, and fall back to existing abstract/body text on failure.

### Task 5: Rendering and Email Delivery

**Files:**
- Create: `src/research_agent/render.py`
- Create: `src/research_agent/delivery/__init__.py`
- Create: `src/research_agent/delivery/email.py`
- Create: `src/research_agent/delivery/notion.py`
- Test: `tests/test_render_email.py`

- [ ] **Step 1: Write failing render/email tests**

```python
from datetime import datetime, timezone

from research_agent.delivery.email import build_email_message
from research_agent.models import Candidate, DailyDigest, DeepReport, QualityScore, RelevanceDecision
from research_agent.render import render_digest_markdown


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
        markdown="## TL;DR\\nUseful paper.",
        text_source="pdf",
    )
    digest = DailyDigest(run_date="2026-06-16", reports=[report], skipped_count=2)
    markdown = render_digest_markdown(digest)
    assert "A Good MI Paper" in markdown
    assert "Overall: 9" in markdown


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_render_email.py -v`

Expected: FAIL because render and delivery modules do not exist yet.

- [ ] **Step 3: Implement Markdown/JSON rendering and SMTP email**

Render a clear Chinese digest and build/send multipart email with Markdown as plain text plus an attachment for JSON output.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_render_email.py -v`

Expected: PASS.

### Task 6: Pipeline, CLI, GitHub Actions, and Documentation

**Files:**
- Create: `src/research_agent/config.py`
- Create: `src/research_agent/__main__.py`
- Create: `src/research_agent/pipeline.py`
- Create: `.github/workflows/daily-research-agent.yml`
- Create: `README_AGENT.md`

- [ ] **Step 1: Implement configuration loading**

Read environment variables, apply defaults, and expose validation for modes that require LLM and SMTP credentials.

- [ ] **Step 2: Implement pipeline orchestration**

Collect candidates, dedupe against state, run LLM stages, download/extract documents, generate reports, write artifacts, optionally send email, and update state.

- [ ] **Step 3: Implement CLI**

Expose:

```bash
python -m research_agent run --dry-run
python -m research_agent collect
python -m research_agent test-email
```

- [ ] **Step 4: Add GitHub Actions workflow**

Install dependencies, run tests, run the agent daily and manually, upload report artifacts, and optionally commit updated state/reports.

- [ ] **Step 5: Write detailed user documentation**

Document local setup, `.env` variables, SMTP examples for QQ/163/enterprise mail, GitHub Secrets, manual workflow runs, generated artifacts, Notion future hooks, troubleshooting, and recommended first-run procedure.

- [ ] **Step 6: Run all tests**

Run: `pytest -v`

Expected: PASS.

- [ ] **Step 7: Run a no-network/no-email smoke command where possible**

Run: `python -m research_agent --help`

Expected: CLI help prints successfully.

## Self-Review

- Spec coverage: The plan covers collection, normalization, state, LLM filtering/scoring/reporting, PDF extraction, rendering, SMTP delivery, GitHub Actions, and user instructions. Notion is represented as a reserved adapter and documented future hook.
- Placeholder scan: No `TBD`, `TODO`, or unresolved placeholder steps are intentionally left in the implementation path.
- Type consistency: Shared model names are `Candidate`, `RelevanceDecision`, `QualityScore`, `DeepReport`, and `DailyDigest`; these names are used consistently across tests and tasks.
