"""Extended tests for AdversarialCouncil — covers edge cases and repr."""

from redteamkit.agent import AgentRole
from redteamkit.council import AdversarialCouncil


def test_council_repr():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
    r = repr(council)
    assert "AdversarialCouncil" in r
    assert "2" in r


def test_council_get_session_not_found():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    assert council.get_session("nonexistent") is None


def test_council_remove_nonexistent_agent():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    assert council.remove_agent("nonexistent-id") is False


def test_council_multiple_sessions():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    r1 = council.run_session("H-001")
    r2 = council.run_session("H-002")
    assert len(council.sessions) == 2
    assert council.get_session(r1.session_id) is not None
    assert council.get_session(r2.session_id) is not None


def test_council_run_with_weaknesses():
    council = AdversarialCouncil(roles=[AgentRole.STRESS_TESTER])
    record = council.run_session(
        "H-003",
        challenges_per_agent=["c1", "c2"],
        weaknesses_per_agent=["w1"],
        confidence=0.8,
    )
    assert record.critiques[0].challenges == ["c1", "c2"]
    assert record.critiques[0].weaknesses == ["w1"]
    assert record.critiques[0].confidence == 0.8
