from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from research_agent.collectors.base import parse_datetime, stable_id
from research_agent.http import get_with_retries
from research_agent.models import Candidate
from research_agent.text import clean_text

LOGGER = logging.getLogger(__name__)


class HuggingFacePapersCollector:
    source_name = "huggingface"

    def __init__(self, session: requests.Session, base_url: str = "https://huggingface.co/papers"):
        self.session = session
        self.base_url = base_url

    def collect(self, lookback_days: int) -> list[Candidate]:
        try:
            response = get_with_retries(self.session, self.base_url, timeout=15, max_retries=1)
        except Exception as exc:
            LOGGER.warning("Hugging Face collection failed: %s", exc)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        candidates: dict[str, Candidate] = {}
        for link in soup.select('a[href^="/papers/"]'):
            title = clean_text(link.get_text(" "))
            href = link.get("href", "")
            if not title or not href:
                continue
            url = urljoin("https://huggingface.co", href)
            if url in candidates:
                continue
            published = self._date_from_url(url)
            if published and published < cutoff:
                continue
            abstract = self._nearby_text(link)
            pdf_url = self._extract_arxiv_pdf(url, abstract)
            candidate = Candidate(
                id=stable_id(self.source_name, url, title),
                source=self.source_name,
                title=title,
                url=url,
                published_at=published,
                abstract=abstract or title,
                pdf_url=pdf_url,
            )
            candidates[url] = candidate
        return list(candidates.values())[:80]

    def _date_from_url(self, url: str) -> datetime | None:
        tail = url.rstrip("/").split("/")[-1]
        if len(tail) >= 10 and tail[4] == "-" and tail[7] == "-":
            return parse_datetime(tail[:10] + "T00:00:00+00:00")
        return None

    def _nearby_text(self, link) -> str:
        parent = link.find_parent(["article", "div", "li"]) or link.parent
        return clean_text(parent.get_text(" ")) if parent else clean_text(link.get_text(" "))

    def _extract_arxiv_pdf(self, url: str, text: str) -> str | None:
        if "arxiv.org/abs/" in text:
            suffix = text.split("arxiv.org/abs/", 1)[1].split()[0].strip(").,")
            return f"https://arxiv.org/pdf/{suffix}.pdf"
        if "/papers/" in url:
            maybe_id = url.rstrip("/").split("/")[-1]
            if maybe_id[:2].isdigit() and "." in maybe_id:
                return f"https://arxiv.org/pdf/{maybe_id}.pdf"
        return None
