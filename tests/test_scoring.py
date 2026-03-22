"""Tests for the HypothesisScorer module."""

from redteamkit.agent import AgentRole, Critique
from redteamkit.scoring import HypothesisScorer, ScoreBreakdown, Verdict


def test_score_without_critiques():
    scorer = HypothesisScorer()
    result = scorer.score("H-001", [])
    assert result.verdict == Verdict.CONDITIONAL
    assert result.critique_count == 0
    assert result.composite_score > 0


def test_score_with_mild_critiques():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id="a1",
            role=AgentRole.CONTRARIAN,
            hypothesis_id="H-001",
            challenges=["Minor concern"],
            confidence=0.3,
        )
    ]
    result = scorer.score("H-001", critiques)
    assert result.verdict in (Verdict.ROBUST, Verdict.CONDITIONAL)
    assert result.critique_count == 1


def test_score_with_severe_critiques():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id=f"a{i}",
            role=AgentRole.STRESS_TESTER,
            hypothesis_id="H-002",
            challenges=[f"Critical flaw {j}" for j in range(5)],
            weaknesses=[f"Weakness {j}" for j in range(4)],
            counter_evidence=[f"Counter {j}" for j in range(3)],
            confidence=0.9,
        )
        for i in range(3)
    ]
    result = scorer.score("H-002", critiques)
    assert result.verdict in (Verdict.WEAK, Verdict.REFUTED)
    assert len(result.notes) > 0


def test_score_breakdown_composite():
    breakdown = ScoreBreakdown(
        evidence_strength=0.8,
        assumption_quality=0.6,
        counter_resilience=0.7,
        internal_consistency=0.9,
    )
    composite = breakdown.composite
    assert 0.0 <= composite <= 1.0
    expected = 0.8 * 0.3 + 0.6 * 0.25 + 0.7 * 0.25 + 0.9 * 0.2
    assert abs(composite - round(expected, 4)) < 0.001


def test_custom_thresholds():
    scorer = HypothesisScorer(thresholds={"robust": 0.9})
    result = scorer.score("H-003", [])
    assert result.verdict != Verdict.ROBUST


def test_notes_high_weakness_count():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id="a1",
            role=AgentRole.ASSUMPTION_HUNTER,
            hypothesis_id="H-004",
            weaknesses=["w1", "w2", "w3", "w4"],
            confidence=0.5,
        )
    ]
    result = scorer.score("H-004", critiques)
    assert any("weakness" in n.lower() for n in result.notes)
