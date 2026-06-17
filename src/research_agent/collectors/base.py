from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Protocol

from research_agent.models import Candidate
from research_agent.text import clean_text


class Collector(Protocol):
    source_name: str

    def collect(self, lookback_days: int) -> list[Candidate]:
        ...


def stable_id(source: str, url: str, title: str = "") -> str:
    key = clean_text(url or title).lower()
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{source}:{digest}"


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        pass
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None
