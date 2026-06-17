from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from research_agent.collectors.base import parse_datetime, stable_id
from research_agent.http import get_with_retries
from research_agent.models import Candidate
from research_agent.text import clean_text

LOGGER = logging.getLogger(__name__)


class WebPageCollector:
    def __init__(self, session: requests.Session, source_name: str, urls: list[str], max_items: int = 60):
        self.session = session
        self.source_name = source_name
        self.urls = urls
        self.max_items = max_items

    def collect(self, lookback_days: int) -> list[Candidate]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        candidates: dict[str, Candidate] = {}
        for index_url in self.urls:
            try:
                response = get_with_retries(self.session, index_url, timeout=15, max_retries=1)
            except Exception as exc:
                LOGGER.warning("%s collection failed for %s: %s", self.source_name, index_url, exc)
                continue
            for candidate in self._parse_index(index_url, response.text):
                if candidate.published_at and candidate.published_at < cutoff:
                    continue
                candidates[candidate.url] = candidate
                if len(candidates) >= self.max_items:
                    return list(candidates.values())
        return list(candidates.values())

    def _parse_index(self, index_url: str, html: str) -> list[Candidate]:
        soup = BeautifulSoup(html, "html.parser")
        candidates: list[Candidate] = []
        base_domain = urlparse(index_url).netloc
        for link in soup.find_all("a", href=True):
            title = clean_text(link.get_text(" "))
            href = link.get("href", "")
            if not self._looks_like_article(title, href):
                continue
            url = urljoin(index_url, href)
            if urlparse(url).netloc and urlparse(url).netloc != base_domain:
                continue
            parent = link.find_parent(["article", "li", "div"]) or link.parent
            text = clean_text(parent.get_text(" ")) if parent else title
            published = self._extract_time(parent)
            candidates.append(
                Candidate(
                    id=stable_id(self.source_name, url, title),
                    source=self.source_name,
                    title=title,
                    url=url,
                    published_at=published,
                    abstract=text or title,
                    body_text=text,
                )
            )
        return candidates

    def _looks_like_article(self, title: str, href: str) -> bool:
        if len(title) < 12 or len(title) > 220:
            return False
        lowered = href.lower()
        blocked = ("#", "mailto:", "javascript:", "/login", "/users/", "/tag")
        if any(lowered.startswith(item) or item in lowered for item in blocked):
            return False
        article_markers = ("/posts/", "/research", "/202", "/blog", "/p/")
        return any(marker in lowered for marker in article_markers)

    def _extract_time(self, node) -> datetime | None:
        if not node:
            return None
        time_node = node.find("time") if hasattr(node, "find") else None
        if time_node:
            return parse_datetime(time_node.get("datetime") or time_node.get_text(" "))
        return None


def default_web_collectors(session: requests.Session, alignment_urls: list[str], anthropic_urls: list[str], circuits_urls: list[str]):
    return [
        WebPageCollector(session, "alignment_forum", alignment_urls),
        WebPageCollector(session, "anthropic", anthropic_urls),
        WebPageCollector(session, "transformer_circuits", circuits_urls),
    ]
