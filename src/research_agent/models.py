from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Candidate:
    id: str
    source: str
    title: str
    url: str
    published_at: datetime | None
    abstract: str
    authors: list[str] = field(default_factory=list)
    pdf_url: str | None = None
    tags: list[str] = field(default_factory=list)
    body_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def recency_key(self) -> datetime:
        return self.published_at or datetime.min.replace(tzinfo=timezone.utc)


@dataclass(slots=True)
class RelevanceDecision:
    relevant: bool
    domain: str
    confidence: int
    reason: str


@dataclass(slots=True)
class QualityScore:
    relevance: float
    novelty: float
    technical_depth: float
    research_value: float
    credibility: float
    overall: float
    priority: str
    reason: str


@dataclass(slots=True)
class DeepReport:
    candidate: Candidate
    relevance: RelevanceDecision
    score: QualityScore
    markdown: str
    text_source: str


@dataclass(slots=True)
class DailyDigest:
    run_date: str
    reports: list[DeepReport]
    skipped_count: int = 0
    candidate_count: int = 0


@dataclass(slots=True)
class RunState:
    processed: dict[str, str] = field(default_factory=dict)


def dataclass_to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "__dataclass_fields__"):
        return {key: dataclass_to_jsonable(val) for key, val in asdict(value).items()}
    if isinstance(value, list):
        return [dataclass_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): dataclass_to_jsonable(val) for key, val in value.items()}
    return value
