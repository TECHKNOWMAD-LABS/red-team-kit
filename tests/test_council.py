"""Tests for the AdversarialCouncil module."""

from redteamkit.agent import AgentRole
from redteamkit.council import AdversarialCouncil


def test_council_default_agents():
    council = AdversarialCouncil()
    assert len(council.agents) == 6


def test_council_custom_roles():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
    assert len(council.agents) == 2


def test_council_add_agent():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    agent = council.add_agent(AgentRole.DEVILS_ADVOCATE)
    assert len(council.agents) == 2
    assert agent.role == AgentRole.DEVILS_ADVOCATE


def test_council_remove_agent():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    agent_id = council.agents[0].agent_id
    assert council.remove_agent(agent_id) is True
    assert len(council.agents) == 0


def test_council_run_session():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
    record = council.run_session("H-TEST-001", confidence=0.6)
    assert record.hypothesis_id == "H-TEST-001"
    assert len(record.critiques) == 2
    assert record.score is not None


def test_council_session_retrieval():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    record = council.run_session("H-TEST-002")
    found = council.get_session(record.session_id)
    assert found is not None
    assert found.session_id == record.session_id


def test_council_reset():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    council.run_session("H-TEST-003")
    council.reset()
    assert len(council.sessions) == 0
