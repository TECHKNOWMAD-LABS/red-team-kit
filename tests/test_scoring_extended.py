"""Extended tests for HypothesisScorer — edge cases and verdict thresholds."""

from redteamkit.agent import AgentRole, Critique
from redteamkit.scoring import HypothesisScorer, ScoreBreakdown, Verdict


def test_verdict_refuted_with_extreme_critiques():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id=f"a{i}",
            role=AgentRole.STRESS_TESTER,
            hypothesis_id="H-EXTREME",
            challenges=[f"c{j}" for j in range(20)],
            weaknesses=[f"w{j}" for j in range(20)],
            counter_evidence=[f"ce{j}" for j in range(20)],
            confidence=0.99,
        )
        for i in range(5)
    ]
    result = scorer.score("H-EXTREME", critiques)
    assert result.verdict == Verdict.REFUTED


def test_high_confidence_agents_noted():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id="a1",
            role=AgentRole.CONTRARIAN,
            hypothesis_id="H-HC",
            challenges=["c1"],
            confidence=0.85,
        ),
        Critique(
            agent_id="a2",
            role=AgentRole.STRESS_TESTER,
            hypothesis_id="H-HC",
            challenges=["c2"],
            confidence=0.9,
        ),
    ]
    result = scorer.score("H-HC", critiques)
    assert any("high-confidence" in n.lower() for n in result.notes)


def test_score_breakdown_all_zeros():
    breakdown = ScoreBreakdown(
        evidence_strength=0.0,
        assumption_quality=0.0,
        counter_resilience=0.0,
        internal_consistency=0.0,
    )
    assert breakdown.composite == 0.0


def test_score_breakdown_all_ones():
    breakdown = ScoreBreakdown(
        evidence_strength=1.0,
        assumption_quality=1.0,
        counter_resilience=1.0,
        internal_consistency=1.0,
    )
    assert breakdown.composite == 1.0


def test_custom_thresholds_all():
    scorer = HypothesisScorer(thresholds={"robust": 0.95, "conditional": 0.7, "weak": 0.4})
    # With no critiques and baseline 0.7, composite should be ~0.7
    result = scorer.score("H-CT", [])
    assert result.verdict == Verdict.CONDITIONAL


def test_score_with_single_critique_no_extras():
    scorer = HypothesisScorer()
    critiques = [
        Critique(
            agent_id="a1",
            role=AgentRole.BLIND_SPOT_FINDER,
            hypothesis_id="H-MIN",
            confidence=0.5,
        )
    ]
    result = scorer.score("H-MIN", critiques)
    assert result.critique_count == 1
    assert result.composite_score > 0
