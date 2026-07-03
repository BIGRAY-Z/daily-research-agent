# Digest Leading Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a leading per-article summary to the final daily report without changing collection, scoring, delivery, GitHub Action configuration, or JSON output.

**Architecture:** Implement this as render-only behavior in `src/research_agent/render.py`. The renderer derives summary rows from existing `DeepReport` data, places them before detailed items in Markdown, and emits an equivalent HTML block before report cards.

**Tech Stack:** Python 3.11, dataclasses, Markdown rendering via `markdown`, tests via `pytest`.

---

### Task 1: Markdown Leading Summary

**Files:**
- Modify: `tests/test_render_email.py`
- Modify: `src/research_agent/render.py`

- [ ] **Step 1: Write the failing Markdown test**

Add this test to `tests/test_render_email.py`:

```python
def test_render_digest_markdown_starts_reports_with_daily_overview():
    candidate = Candidate(
        id="id-1",
        source="arxiv",
        title="A Good MI Paper",
        url="https://example.com/paper",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="abstract fallback",
    )
    report = DeepReport(
        candidate=candidate,
        relevance=RelevanceDecision(True, "Mechanistic Interpretability", 9, "relevant"),
        score=QualityScore(9, 8, 9, 9, 8, 9, "must_read", "strong selection reason"),
        markdown="## TL;DR\n这篇文章提出了一个清晰的机制解释方法。\n\n## Details\nLong report.",
        text_source="pdf",
    )
    digest = DailyDigest(run_date="2026-06-16", reports=[report], skipped_count=2)

    markdown = render_digest_markdown(digest)

    assert markdown.index("## 今日速览") < markdown.index("## Top Items")
    assert "### 1. A Good MI Paper" in markdown
    assert "- 分数: 9" in markdown
    assert "- 简单概述: 这篇文章提出了一个清晰的机制解释方法。" in markdown
    assert "- 入选理由: strong selection reason" in markdown
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `pytest tests/test_render_email.py::test_render_digest_markdown_starts_reports_with_daily_overview -q`

Expected: FAIL because `## 今日速览` is not present.

- [ ] **Step 3: Implement Markdown summary helpers**

In `src/research_agent/render.py`, add helper functions that:

```python
def overview_from_report(report: DeepReport) -> str:
    # Prefer TL;DR section, then first paragraph, then candidate abstract/body.
```

and update `render_digest_markdown()` to insert:

```markdown
## 今日速览

### 1. {title}

- 分数: {score}
- 简单概述: {overview}
- 入选理由: {reason}
```

before `## Top Items`.

- [ ] **Step 4: Run the focused Markdown test and verify it passes**

Run: `pytest tests/test_render_email.py::test_render_digest_markdown_starts_reports_with_daily_overview -q`

Expected: PASS.

### Task 2: HTML Leading Summary

**Files:**
- Modify: `tests/test_render_email.py`
- Modify: `src/research_agent/render.py`

- [ ] **Step 1: Write the failing HTML test**

Add this test to `tests/test_render_email.py`:

```python
def test_render_digest_html_contains_daily_overview_before_cards():
    candidate = Candidate(
        id="id-1",
        source="arxiv",
        title="A Good MI Paper",
        url="https://example.com/paper",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="abstract fallback",
    )
    report = DeepReport(
        candidate=candidate,
        relevance=RelevanceDecision(True, "Mechanistic Interpretability", 9, "relevant"),
        score=QualityScore(9, 8, 9, 9, 8, 9, "must_read", "strong selection reason"),
        markdown="## TL;DR\n这篇文章提出了一个清晰的机制解释方法。\n\n## Details\nLong report.",
        text_source="pdf",
    )
    digest = DailyDigest(run_date="2026-06-16", reports=[report], skipped_count=2)

    html = render_digest_html(digest)

    assert html.index("今日速览") < html.index("report-card")
    assert "A Good MI Paper" in html
    assert "这篇文章提出了一个清晰的机制解释方法。" in html
    assert "strong selection reason" in html
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `pytest tests/test_render_email.py::test_render_digest_html_contains_daily_overview_before_cards -q`

Expected: FAIL because `今日速览` is not present before cards.

- [ ] **Step 3: Implement HTML summary rendering**

In `src/research_agent/render.py`, add a `render_overview_html()` helper or equivalent local block that escapes title, URL, overview, and reason. Insert it after the `.topbar` section and before `cards`.

- [ ] **Step 4: Run the focused HTML test and verify it passes**

Run: `pytest tests/test_render_email.py::test_render_digest_html_contains_daily_overview_before_cards -q`

Expected: PASS.

### Task 3: Verification And Push

**Files:**
- Verify all changed files.

- [ ] **Step 1: Run render tests**

Run: `pytest tests/test_render_email.py -q`

Expected: all tests in the file pass.

- [ ] **Step 2: Run full test suite**

Run: `pytest -q`

Expected: all tests pass.

- [ ] **Step 3: Review diff**

Run: `git diff --stat && git diff -- tests/test_render_email.py src/research_agent/render.py`

Expected: only render/test/doc changes related to the leading summary.

- [ ] **Step 4: Commit implementation**

Run:

```bash
git add tests/test_render_email.py src/research_agent/render.py docs/superpowers/plans/2026-07-03-digest-leading-summary.md
git commit -m "feat: add leading report summaries"
```

- [ ] **Step 5: Push to origin**

Run: `git push origin main`

Expected: push succeeds.
