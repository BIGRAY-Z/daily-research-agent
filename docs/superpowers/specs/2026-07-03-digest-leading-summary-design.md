# Digest Leading Summary Design

## Context

The daily research agent already collects candidates, scores them, generates deep reports, renders `digest.md` and `digest.html`, creates a PDF from the HTML, and sends the Markdown digest as the email body. The requested change is to add a summary for every selected article at the very beginning of the final report while preserving the existing GitHub Action, configuration, pipeline, and delivery behavior.

## Decision

Implement the feature entirely in the render layer. `src/research_agent/render.py` will derive a leading per-article overview from each existing `DeepReport`:

- Score: use `report.score.overall` formatted with the existing `format_score()`.
- Chinese simple overview: prefer the report's `TL;DR` section, then fall back to the first meaningful paragraph in the report Markdown, then to the candidate abstract/body text.
- Selection reason: use the existing stage 2 `report.score.reason`.

The Markdown email body will place this section after the run statistics and before the detailed `Top Items` section. The HTML report will render an equivalent leading section after the topbar and before the per-article cards, so the PDF generated from HTML includes the same summary.

## Scope

In scope:

- Add `## 今日速览` to rendered Markdown when reports exist.
- Add an equivalent HTML summary block when reports exist.
- Escape HTML values and keep existing math/Markdown rendering behavior untouched.
- Keep fallback reports and collect-only reports supported by deriving summaries from available report/candidate text.
- Add tests for Markdown and HTML output.

Out of scope:

- No new LLM call.
- No new environment variable or GitHub Action configuration.
- No JSON schema changes.
- No changes to candidate selection, scoring, report generation, state handling, or email sending.

## Data Flow

`DailyDigest` and `DeepReport` remain unchanged. The new render helpers compute display-only summary rows at render time. `write_digest_artifacts()` continues to write `digest.md`, `digest.html`, and `digest.json`; only the Markdown and HTML render output changes. Email sending continues to call `render_digest_markdown(digest)`.

## Error Handling

Summary rendering must never block report delivery. If the report body has no useful `TL;DR` or paragraph, the renderer falls back to candidate abstract/body text. If that is also empty, it emits `暂无可用概述。`. Empty score reasons fall back to `未提供评分理由。`.

## Testing

Add focused tests in `tests/test_render_email.py`:

- Markdown output includes `## 今日速览` before `## Top Items` and includes score, overview, and selection reason.
- HTML output includes the leading summary block before report cards and includes the same score, overview, and selection reason.

Existing tests continue to cover email building, Markdown-to-HTML conversion, and PDF generation.
