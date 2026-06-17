from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests

from research_agent.collectors.base import parse_datetime
from research_agent.http import get_with_retries
from research_agent.models import Candidate
from research_agent.text import clean_text

LOGGER = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"

DEFAULT_TERMS = [
    '"mechanistic interpretability"',
    '"sparse autoencoder"',
    '"circuit tracing"',
    '"attribution graph"',
    '"activation steering"',
    '"representation engineering"',
    '"AI alignment"',
    "monosemanticity",
    "deception",
]


class ArxivCollector:
    source_name = "arxiv"

    def __init__(self, session: requests.Session, terms: list[str] | None = None, max_results: int = 80):
        self.session = session
        self.terms = terms or DEFAULT_TERMS
        self.max_results = max_results

    def collect(self, lookback_days: int) -> list[Candidate]:
        query = " OR ".join([f"all:{term}" for term in self.terms])
        params = {
            "search_query": query,
            "start": 0,
            "max_results": self.max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{ARXIV_API_URL}?{urlencode(params)}"
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        try:
            response = get_with_retries(self.session, url, timeout=20, max_retries=1)
            root = ET.fromstring(response.text)
        except Exception as exc:
            LOGGER.warning("arXiv collection failed: %s", exc)
            return []

        candidates: list[Candidate] = []
        for entry in root.findall(f"{ATOM}entry"):
            candidate = self._parse_entry(entry)
            if candidate.published_at and candidate.published_at < cutoff:
                continue
            candidates.append(candidate)
        return candidates

    def _parse_entry(self, entry: ET.Element) -> Candidate:
        title = clean_text(entry.findtext(f"{ATOM}title"))
        abstract = clean_text(entry.findtext(f"{ATOM}summary"))
        url = clean_text(entry.findtext(f"{ATOM}id"))
        published = parse_datetime(entry.findtext(f"{ATOM}published"))
        authors = [
            clean_text(author.findtext(f"{ATOM}name"))
            for author in entry.findall(f"{ATOM}author")
            if clean_text(author.findtext(f"{ATOM}name"))
        ]
        tags = [category.attrib.get("term", "") for category in entry.findall(f"{ATOM}category")]
        pdf_url = None
        for link in entry.findall(f"{ATOM}link"):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href")
                break
        arxiv_id = url.rstrip("/").split("/")[-1]
        return Candidate(
            id=f"arxiv:{arxiv_id}",
            source=self.source_name,
            title=title,
            url=url,
            published_at=published,
            abstract=abstract,
            authors=authors,
            pdf_url=pdf_url,
            tags=[tag for tag in tags if tag],
        )
