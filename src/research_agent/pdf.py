from __future__ import annotations

import io
import logging

import requests

from research_agent.http import get_with_retries
from research_agent.text import clean_text

LOGGER = logging.getLogger(__name__)


def download_pdf(session: requests.Session, url: str, max_bytes: int = 35_000_000) -> bytes:
    response = get_with_retries(session, url, timeout=60, stream=True)
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=1024 * 256):
        if not chunk:
            continue
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"PDF exceeds size limit: {url}")
        chunks.append(chunk)
    return b"".join(chunks)


def extract_pdf_text(pdf_bytes: bytes, max_pages: int = 80) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for page in reader.pages[:max_pages]:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:
            LOGGER.warning("PDF page extraction failed: %s", exc)
    return clean_text("\n".join(pages))


def fetch_pdf_text(session: requests.Session, url: str) -> str:
    return extract_pdf_text(download_pdf(session, url))
