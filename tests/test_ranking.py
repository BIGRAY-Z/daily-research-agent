from datetime import datetime, timezone

from research_agent.models import Candidate, QualityScore
from research_agent.config import AppConfig
from research_agent.models import RelevanceDecision
from research_agent.pipeline import prepare_report_text, score_candidate, select_top_candidates


def candidate(idx, score):
    return (
        Candidate(
            id=f"id-{idx}",
            source="test",
            title=f"paper {idx}",
            url=f"https://example.com/{idx}",
            published_at=datetime(2026, 6, idx, tzinfo=timezone.utc),
            abstract="abstract",
        ),
        QualityScore(
            relevance=score,
            novelty=score,
            technical_depth=score,
            research_value=score,
            credibility=score,
            overall=score,
            priority="strong",
            reason="reason",
        ),
    )


def test_select_top_candidates_limits_and_sorts():
    ranked = [candidate(i, float(i)) for i in range(1, 9)]
    selected = select_top_candidates(ranked, max_reports=6)
    assert [item[0].id for item in selected] == ["id-8", "id-7", "id-6", "id-5", "id-4", "id-3"]


def test_select_top_candidates_handles_missing_dates():
    dated = candidate(1, 8.0)
    undated_candidate, undated_score = candidate(2, 8.0)
    undated_candidate.published_at = None
    selected = select_top_candidates([(undated_candidate, undated_score), dated], 2)
    assert [item[0].id for item in selected] == ["id-1", "id-2"]


def test_prepare_report_text_truncates_document():
    text = prepare_report_text("a" * 100, max_chars=25)
    assert len(text) <= 40
    assert "[truncated]" in text


def test_score_candidate_calls_llm_once():
    class FakeLLM:
        calls = 0

        def chat_json(self, model, system_prompt, user_prompt):
            self.calls += 1
            return {
                "relevance": 9,
                "novelty": 8,
                "technical_depth": 7,
                "research_value": 9,
                "credibility": 8,
                "overall": 9,
                "priority": "strong",
                "reason": "good",
            }

    llm = FakeLLM()
    candidate_obj, _ = candidate(1, 9.0)

    score = score_candidate(
        llm,
        AppConfig(stage2_model="stage2"),
        candidate_obj,
        RelevanceDecision(True, "AI Alignment", 9, "relevant"),
    )

    assert llm.calls == 1
    assert score.overall == 9
