"""Tests for the RedTeamAgent module."""

from redteamkit.agent import AgentRole, Critique, RedTeamAgent


def test_agent_creation_default_id():
    agent = RedTeamAgent(role=AgentRole.DEVILS_ADVOCATE)
    assert agent.role == AgentRole.DEVILS_ADVOCATE
    assert len(agent.agent_id) == 12


def test_agent_creation_custom_id():
    agent = RedTeamAgent(role=AgentRole.CONTRARIAN, agent_id="custom-123")
    assert agent.agent_id == "custom-123"


def test_agent_critique_produces_result():
    agent = RedTeamAgent(role=AgentRole.STRESS_TESTER)
    critique = agent.critique(
        hypothesis_id="H-001",
        challenges=["Revenue assumptions are untested"],
        weaknesses=["No sensitivity analysis"],
        confidence=0.7,
    )
    assert isinstance(critique, Critique)
    assert critique.hypothesis_id == "H-001"
    assert critique.confidence == 0.7
    assert len(critique.challenges) == 1


def test_agent_tracks_critiques():
    agent = RedTeamAgent(role=AgentRole.ASSUMPTION_HUNTER)
    agent.critique(hypothesis_id="H-001", confidence=0.5)
    agent.critique(hypothesis_id="H-002", confidence=0.6)
    assert len(agent.critiques) == 2


def test_agent_reset_clears_critiques():
    agent = RedTeamAgent(role=AgentRole.BLIND_SPOT_FINDER)
    agent.critique(hypothesis_id="H-001", confidence=0.5)
    agent.reset()
    assert len(agent.critiques) == 0


def test_agent_repr():
    agent = RedTeamAgent(role=AgentRole.SCENARIO_EXPLORER, agent_id="abc")
    assert "scenario_explorer" in repr(agent)
    assert "abc" in repr(agent)
