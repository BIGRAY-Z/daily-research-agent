# Daily AI Safety Research Agent Design

Date: 2026-06-16

## Goal

Build a from-scratch agent that runs daily without a personal machine, collects high-quality recent work about Mechanistic Interpretability, AI Alignment, and Representation Engineering, filters and ranks candidates with OpenAI-compatible LLM APIs, produces deep reading reports for the top six items, and sends the report by email.

The default deployment target is GitHub Actions. The default delivery target is SMTP email for QQ/163/enterprise-style mailboxes. Notion is reserved as a future delivery adapter with documented integration points.

## User Decisions

- Project starts from scratch in `/public/home/zhangrm2022/lately_work`.
- Default scheduler: GitHub Actions.
- API protocol: OpenAI-compatible chat API.
- Delivery: email first; Notion reserved.
- Email provider class: regular SMTP mailbox, such as QQ, 163, or enterprise email.
- Collection window: last 3 days by default, to avoid time-zone and source-update misses.

## Non-Goals for MVP

- No always-on web service.
- No interactive dashboard.
- No mandatory database server.
- No direct PDF upload dependency, because OpenAI-compatible gateways vary in file support.
- No hard-coded vendor-specific gateway details.

## Architecture

The project is a Python CLI with independent modules:

- `collectors`: source-specific fetchers for arXiv, Hugging Face Papers, Alignment Forum, Anthropic Research, and Transformer Circuits.
- `models`: shared dataclasses for candidates, LLM decisions, scores, reports, and run state.
- `llm`: OpenAI-compatible chat client with JSON-output helpers and retry handling.
- `pipeline`: orchestration for collection, normalization, deduplication, filtering, scoring, report generation, and delivery.
- `pdf`: PDF download and local text extraction.
- `render`: Markdown and JSON report rendering.
- `delivery`: SMTP email sender, plus a placeholder adapter for Notion.
- `config`: environment-variable based configuration.

Each module has a narrow contract so individual sources and delivery methods can be replaced without changing the core pipeline.

## Data Flow

1. Load configuration from environment variables and CLI flags.
2. Load state from `data/state.json`.
3. Collect candidates from the last `LOOKBACK_DAYS`, default `3`.
4. Normalize each item into a `Candidate`.
5. Deduplicate by stable IDs: arXiv ID, canonical URL, or content hash.
6. Run stage 1 LLM relevance classification on title and abstract.
7. Keep relevant candidates with sufficient confidence.
8. Run stage 2 LLM quality scoring and rank candidates.
9. Select top `MAX_REPORTS`, default `6`.
10. Download PDF when available; otherwise extract article text from HTML.
11. Generate a deep Markdown report per selected item with the high-quality model.
12. Render a daily digest.
13. Send the digest through SMTP.
14. Save updated state and report artifacts.

## Source Strategy

### arXiv

Use the official Atom API. Query with topic-oriented search terms and date constraints. Prefer categories `cs.AI`, `cs.CL`, `cs.LG`, `cs.CY`, `stat.ML`, and related terms in title/abstract.

Initial query terms include:

- `mechanistic interpretability`
- `sparse autoencoder`
- `SAE`
- `circuit tracing`
- `attribution graph`
- `activation steering`
- `representation engineering`
- `AI alignment`
- `ELK`
- `deception`
- `model organisms`
- `monosemanticity`

### Hugging Face Papers

Fetch the Daily Papers listing and linked paper pages. Extract title, short summary, date, tags, arXiv link when present, and PDF URL when discoverable. Because this page may change structure, failures should degrade gracefully and not fail the entire run.

### Alignment Forum

Prefer a GraphQL/latest-posts route if accessible. If it fails, use the public page HTML fallback. Extract title, URL, date, excerpt, and available body text for high-ranking posts.

### Anthropic and Transformer Circuits

Fetch public research pages and transformer-circuits pages. Treat official interpretability/alignment posts as high-priority candidates, but still run LLM classification and scoring. Source URLs are configurable so new official feeds or pages can be added without code changes.

## LLM Stages

### Stage 1: Relevance Filter

Input is title, abstract/excerpt, source, and URL. Output must be strict JSON:

```json
{
  "relevant": true,
  "domain": "Mechanistic Interpretability",
  "confidence": 8,
  "reason": "..."
}
```

Accepted domains:

- `Mechanistic Interpretability`
- `AI Alignment`
- `Representation Engineering`
- `Adjacent`

Candidates with `relevant=false` are dropped. The default confidence threshold is `6`.

### Stage 2: Quality Scoring

Input is title, abstract/excerpt, source, URL, and stage 1 decision. Output is strict JSON with numeric scores:

- `relevance`: domain fit.
- `novelty`: whether the core idea is new or meaningfully advances the field.
- `technical_depth`: method and evidence quality.
- `research_value`: value for future research or implementation.
- `credibility`: strength of source, experiments, and claims.
- `overall`: final 0-10 score.
- `reason`: concise rationale.
- `priority`: `must_read`, `strong`, `maybe`, or `skip`.

The pipeline selects the top six by `overall`, then by `relevance`, then by recency.

### Stage 3: Deep Report

For each selected item, download and extract PDF text if possible. If no PDF exists, extract article HTML text. Chunk long documents and ask the high-quality model to synthesize across chunks.

The report prompt must cover:

1. TL;DR.
2. Core contributions.
3. Research question, background, importance, and value.
4. Prior work and why it was insufficient.
5. Reconstructed author thinking path before the method.
6. Core intuition.
7. Method pipeline with a concrete example.
8. Mathematical derivation and required theory background when applicable.
9. Experimental design: question, experiment, answer.
10. Takeaways.
11. Most fragile assumption.
12. One-week minimal reproduction experiment.
13. Possible counterexample design.
14. Novel follow-up idea based on limitations and needs.

## Configuration

Required environment variables:

- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `STAGE1_MODEL`
- `STAGE2_MODEL`
- `REPORT_MODEL`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

Optional variables:

- `LOOKBACK_DAYS`, default `3`
- `MAX_REPORTS`, default `6`
- `STAGE1_CONFIDENCE_THRESHOLD`, default `6`
- `REPORT_LANGUAGE`, default `zh`
- `SEND_EMAIL`, default `true`
- `STATE_PATH`, default `data/state.json`
- `REPORT_DIR`, default `reports`
- `ANTHROPIC_URLS`
- `TRANSFORMER_CIRCUITS_URLS`
- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`

## State and Artifacts

The agent writes:

- `data/state.json`: processed IDs and timestamps.
- `reports/YYYY-MM-DD/digest.md`: final daily email body.
- `reports/YYYY-MM-DD/digest.json`: structured output.
- `reports/YYYY-MM-DD/items/*.md`: one deep report per item.
- `reports/YYYY-MM-DD/raw/`: optional raw extracted text and candidate JSON.

GitHub Actions can upload reports as artifacts. Optionally, the workflow can commit `data/state.json` and `reports/` back to the repository.

## Error Handling

- One source failure should not fail the whole run.
- LLM JSON parse failures should retry with a stricter repair prompt.
- PDF download failures should fall back to abstract or HTML text.
- Email failure should fail the workflow after reports are generated.
- Empty candidate days should send a short no-new-items email only if configured.
- Rate-limit errors should use exponential backoff and a small concurrency limit.

## Testing

Use focused tests with mocked network and LLM clients:

- Candidate normalization and deduplication.
- Stage 1 JSON parsing and fallback repair.
- Stage 2 ranking and top-six selection.
- PDF text extraction fallback behavior.
- Markdown digest rendering.
- SMTP message construction without sending.

Manual verification:

- Run local dry-run with `SEND_EMAIL=false`.
- Run local email test with one synthetic report.
- Trigger GitHub Actions manually with `workflow_dispatch`.

## Deployment

GitHub Actions workflow:

- Runs daily on cron.
- Supports manual run.
- Installs Python dependencies.
- Runs tests.
- Runs `python -m research_agent run`.
- Uploads reports as artifacts.
- Optionally commits state and report artifacts back to the repository.

Secrets are configured in GitHub repository settings. No secrets are stored in files.

## Future Extensions

- Notion adapter writes one page per daily digest and one child page per report.
- Add user feedback labels to tune source weights and scoring.
- Add a lightweight SQLite database if state grows beyond JSON.
- Add citation graph enrichment through Semantic Scholar/OpenAlex.
- Add source-specific parsing for new labs and newsletters.
