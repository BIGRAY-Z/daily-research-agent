from __future__ import annotations

import time

import requests


DEFAULT_USER_AGENT = "daily-research-agent/0.1 (+https://github.com/)"


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    return session


def get_with_retries(
    session: requests.Session,
    url: str,
    *,
    timeout: int = 30,
    max_retries: int = 3,
    **kwargs,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"GET failed for {url}: {last_error}")
