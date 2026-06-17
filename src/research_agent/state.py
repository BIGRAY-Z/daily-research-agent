from __future__ import annotations

import json
from pathlib import Path

from research_agent.models import Candidate, RunState


def load_state(path: str | Path) -> RunState:
    state_path = Path(path)
    if not state_path.exists():
        return RunState()
    with state_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    processed = raw.get("processed", {})
    if not isinstance(processed, dict):
        processed = {}
    return RunState(processed={str(key): str(value) for key, value in processed.items()})


def save_state(path: str | Path, state: RunState) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"processed": state.processed}
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def candidate_seen(state: RunState, candidate: Candidate) -> bool:
    return candidate.id in state.processed


def mark_candidate_seen(state: RunState, candidate: Candidate, timestamp: str) -> None:
    state.processed[candidate.id] = timestamp
