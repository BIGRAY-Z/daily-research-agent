from __future__ import annotations

import json
import re
import unicodedata
from typing import Any


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


MOJIBAKE_MARKERS = ("Ã", "Â", "â", "ä", "å", "æ", "ç", "è", "é", "ï¼", "ã€")


def repair_mojibake(value: str) -> str:
    if not value or not any(marker in value for marker in MOJIBAKE_MARKERS):
        return value
    try:
        raw = _mojibake_to_bytes(value)
        repaired = raw.decode("utf-8")
    except UnicodeError:
        return value
    if _looks_less_broken(value, repaired):
        return repaired
    return value


def _mojibake_to_bytes(value: str) -> bytes:
    output = bytearray()
    for character in value:
        codepoint = ord(character)
        if codepoint <= 255:
            output.append(codepoint)
            continue
        output.extend(character.encode("cp1252"))
    return bytes(output)


def _looks_less_broken(original: str, repaired: str) -> bool:
    original_score = sum(original.count(marker) for marker in MOJIBAKE_MARKERS)
    repaired_score = sum(repaired.count(marker) for marker in MOJIBAKE_MARKERS)
    return repaired_score < original_score


def repair_json_strings(value: Any) -> Any:
    if isinstance(value, str):
        return repair_mojibake(value)
    if isinstance(value, list):
        return [repair_json_strings(item) for item in value]
    if isinstance(value, dict):
        return {key: repair_json_strings(item) for key, item in value.items()}
    return value


def slugify(value: str, max_length: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if len(slug) > max_length:
        slug = slug[:max_length].strip("-")
    return slug or "item"


def extract_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return json.loads(fenced.group(1))

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return repair_json_strings(value)
    raise ValueError("No JSON object found in LLM response")


def truncate_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 20].rstrip() + "\n...[truncated]"
