from datetime import datetime, timezone

from research_agent.models import Candidate
from research_agent.state import candidate_seen, load_state, mark_candidate_seen, save_state


def make_candidate():
    return Candidate(
        id="arxiv:2606.00001",
        source="arxiv",
        title="Mechanistic Interpretability Test",
        url="https://arxiv.org/abs/2606.00001",
        published_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
        abstract="test",
    )


def test_state_round_trip(tmp_path):
    path = tmp_path / "state.json"
    state = load_state(path)
    candidate = make_candidate()
    mark_candidate_seen(state, candidate, "2026-06-16T00:00:00+00:00")
    save_state(path, state)
    loaded = load_state(path)
    assert candidate_seen(loaded, candidate)
