"""Property-based tests using Hypothesis — invariant verification across random inputs."""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from redteamkit.agent import AgentRole, Critique, RedTeamAgent
from redteamkit.scoring import HypothesisScorer, ScoreBreakdown, Verdict
from redteamkit.council import AdversarialCouncil
from redteamkit.report import Report, ReportGenerator


# -- Strategies --

valid_hypothesis_id = st.text(min_size=1, max_size=200).filter(lambda s: s.strip())
confidence_float = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
challenge_list = st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=10)
role_strategy = st.sampled_from(list(AgentRole))
score_float = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


class TestScoreBreakdownProperties:
    """Property: composite score is always in [0.0, 1.0]."""

    @given(
        evidence=score_float,
        assumption=score_float,
        counter=score_float,
        consistency=score_float,
    )
    def test_composite_always_in_range(self, evidence, assumption, counter, consistency):
        breakdown = ScoreBreakdown(
            evidence_strength=evidence,
            assumption_quality=assumption,
            counter_resilience=counter,
            internal_consistency=consistency,
        )
        assert 0.0 <= breakdown.composite <= 1.0

    @given(
        evidence=score_float,
        assumption=score_float,
        counter=score_float,
        consistency=score_float,
    )
    def test_composite_is_weighted_average(self, evidence, assumption, counter, consistency):
        breakdown = ScoreBreakdown(
            evidence_strength=evidence,
            assumption_quality=assumption,
            counter_resilience=counter,
            internal_consistency=consistency,
        )
        expected = round(
            0.3 * evidence + 0.25 * assumption + 0.25 * counter + 0.2 * consistency,
            4,
        )
        assert abs(breakdown.composite - expected) < 1e-6


class TestScorerProperties:
    """Property: scorer always returns valid verdict regardless of input."""

    @given(
        hypothesis_id=valid_hypothesis_id,
        confidence=confidence_float,
        num_challenges=st.integers(min_value=0, max_value=20),
        num_weaknesses=st.integers(min_value=0, max_value=20),
        num_counter=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=50)
    def test_verdict_always_valid(
        self, hypothesis_id, confidence, num_challenges, num_weaknesses, num_counter
    ):
        scorer = HypothesisScorer()
        critiques = [
            Critique(
                agent_id="prop-agent",
                role=AgentRole.CONTRARIAN,
                hypothesis_id=hypothesis_id,
                challenges=[f"c{i}" for i in range(num_challenges)],
                weaknesses=[f"w{i}" for i in range(num_weaknesses)],
                counter_evidence=[f"ce{i}" for i in range(num_counter)],
                confidence=confidence,
            )
        ]
        result = scorer.score(hypothesis_id, critiques)
        assert result.verdict in list(Verdict)
        assert 0.0 <= result.composite_score <= 1.0
        assert result.critique_count == 1

    @given(hypothesis_id=valid_hypothesis_id)
    @settings(max_examples=30)
    def test_empty_critiques_never_crash(self, hypothesis_id):
        scorer = HypothesisScorer()
        result = scorer.score(hypothesis_id, [])
        assert result.verdict in list(Verdict)
        assert result.critique_count == 0


class TestAgentProperties:
    """Property: agent operations never crash on valid inputs."""

    @given(
        role=role_strategy,
        hypothesis_id=valid_hypothesis_id,
        confidence=confidence_float,
        challenges=challenge_list,
    )
    @settings(max_examples=50)
    def test_critique_round_trip(self, role, hypothesis_id, confidence, challenges):
        agent = RedTeamAgent(role=role)
        critique = agent.critique(
            hypothesis_id=hypothesis_id,
            challenges=challenges,
            confidence=confidence,
        )
        assert critique.hypothesis_id == hypothesis_id
        assert critique.confidence == confidence
        assert critique.challenges == challenges
        assert critique.role == role

    @given(role=role_strategy, num_critiques=st.integers(min_value=0, max_value=20))
    @settings(max_examples=20)
    def test_reset_always_clears(self, role, num_critiques):
        agent = RedTeamAgent(role=role)
        for i in range(num_critiques):
            agent.critique(hypothesis_id=f"H-{i}", confidence=0.5)
        assert len(agent.critiques) == num_critiques
        agent.reset()
        assert len(agent.critiques) == 0


class TestCritiqueSerializationRoundTrip:
    """Property: Critique serializes and deserializes without loss."""

    @given(
        role=role_strategy,
        hypothesis_id=valid_hypothesis_id,
        confidence=confidence_float,
        challenges=challenge_list,
    )
    @settings(max_examples=30)
    def test_json_round_trip(self, role, hypothesis_id, confidence, challenges):
        original = Critique(
            agent_id="rt-001",
            role=role,
            hypothesis_id=hypothesis_id,
            challenges=challenges,
            confidence=confidence,
        )
        json_str = original.model_dump_json()
        restored = Critique.model_validate_json(json_str)
        assert restored == original

    @given(
        role=role_strategy,
        hypothesis_id=valid_hypothesis_id,
        confidence=confidence_float,
    )
    @settings(max_examples=30)
    def test_dict_round_trip(self, role, hypothesis_id, confidence):
        original = Critique(
            agent_id="rt-002",
            role=role,
            hypothesis_id=hypothesis_id,
            confidence=confidence,
        )
        d = original.model_dump()
        restored = Critique.model_validate(d)
        assert restored == original


class TestReportProperties:
    """Property: report generation never crashes on valid sessions."""

    @given(num_sessions=st.integers(min_value=0, max_value=10))
    @settings(max_examples=15)
    def test_report_from_any_session_count(self, num_sessions):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        for i in range(num_sessions):
            council.run_session(f"H-PROP-{i}", confidence=0.5)
        gen = ReportGenerator()
        report = gen.generate(council.sessions)
        assert isinstance(report, Report)
        assert report.metadata["session_count"] == num_sessions
        # Overview + per-session + verdict = 2 + num_sessions
        assert len(report.sections) == 2 + num_sessions
