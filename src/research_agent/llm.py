from __future__ import annotations

import time
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any

import requests

from research_agent.text import extract_json_object, repair_mojibake


class LLMError(RuntimeError):
    pass


@dataclass(slots=True)
class LLMClient:
    base_url: str
    api_key: str
    timeout_seconds: int = 120
    max_retries: int = 3

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def chat(self, model: str, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
                response.raise_for_status()
                try:
                    data = response.json()
                except (ValueError, JSONDecodeError) as exc:
                    content_type = response.headers.get("content-type", "unknown")
                    prefix = response.text[:300].replace("\n", "\\n")
                    raise LLMError(
                        "LLM endpoint returned a non-JSON response. "
                        f"url={url}, status={response.status_code}, content_type={content_type}, "
                        f"body_prefix={prefix!r}. Check OPENAI_BASE_URL; OpenAI-compatible API roots "
                        "usually ends with /v1."
                    ) from exc
                return repair_mojibake(data["choices"][0]["message"]["content"])
            except Exception as exc:  # requests and schema errors should share retry behavior.
                last_error = exc
                if attempt < self.max_retries - 1:
                    time.sleep(self._retry_delay_seconds(exc, attempt))
        raise LLMError(f"LLM request failed after {self.max_retries} attempts: {last_error}")

    def _retry_delay_seconds(self, exc: Exception, attempt: int) -> int:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code == 429 or (isinstance(status_code, int) and status_code >= 500):
            return 8 * (2**attempt)
        return 2**attempt

    def chat_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        raw = self.chat(model=model, messages=messages, temperature=temperature)
        try:
            return extract_json_object(raw)
        except Exception:
            repair_messages = messages + [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": "上一个回答不是可解析的严格 JSON。请只输出一个 JSON object，不要 Markdown，不要解释。",
                },
            ]
            repaired = self.chat(model=model, messages=repair_messages, temperature=0.0)
            return extract_json_object(repaired)
