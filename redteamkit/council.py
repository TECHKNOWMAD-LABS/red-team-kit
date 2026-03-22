"""Adversarial council that orchestrates red-team agents to stress-test hypotheses."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from redteamkit.agent import AgentRole, Critique, RedTeamAgent
from redteamkit.scoring import HypothesisScore, HypothesisScorer


class SessionRecord(BaseModel):
    session_id: str
    hypothesis_id: str
    critiques: list[Critique] = Field(default_factory=list)
    score: HypothesisScore | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdversarialCouncil:
    """Manages a panel of adversarial agents that collectively evaluate hypotheses."""

    DEFAULT_ROLES: list[AgentRole] = [
        AgentRole.DEVILS_ADVOCATE,
        AgentRole.CONTRARIAN,
        AgentRole.STRESS_TESTER,
        AgentRole.ASSUMPTION_HUNTER,
        AgentRole.BLIND_SPOT_FINDER,
        AgentRole.SCENARIO_EXPLORER,
    ]

    def __init__(
        self,
        roles: list[AgentRole] | None = None,
        scorer: HypothesisScorer | None = None,
    ) -> None:
        selected_roles = roles or self.DEFAULT_ROLES
        self.agents = [RedTeamAgent(role=r) for r in selected_roles]
        self.scorer = scorer or HypothesisScorer()
        self._sessions: list[SessionRecord] = []

    @property
    def sessions(self) -> list[SessionRecord]:
        return list(self._sessions)

    def add_agent(self, role: AgentRole) -> RedTeamAgent:
        agent = RedTeamAgent(role=role)
        self.agents.append(agent)
        return agent

    def remove_agent(self, agent_id: str) -> bool:
        before = len(self.agents)
        self.agents = [a for a in self.agents if a.agent_id != agent_id]
        return len(self.agents) < before

    def run_session(
        self,
        hypothesis_id: str,
        challenges_per_agent: list[str] | None = None,
        weaknesses_per_agent: list[str] | None = None,
        confidence: float = 0.5,
    ) -> SessionRecord:
        """Run a full adversarial session where all agents critique a hypothesis."""
        session_id = uuid.uuid4().hex[:12]
        critiques: list[Critique] = []

        for agent in self.agents:
            critique = agent.critique(
                hypothesis_id=hypothesis_id,
                challenges=challenges_per_agent or [f"Challenge from {agent.role.value}"],
                weaknesses=weaknesses_per_agent,
                confidence=confidence,
            )
            critiques.append(critique)

        score = self.scorer.score(hypothesis_id, critiques)
        record = SessionRecord(
            session_id=session_id,
            hypothesis_id=hypothesis_id,
            critiques=critiques,
            score=score,
        )
        self._sessions.append(record)
        return record

    def get_session(self, session_id: str) -> SessionRecord | None:
        for s in self._sessions:
            if s.session_id == session_id:
                return s
        return None

    def reset(self) -> None:
        for agent in self.agents:
            agent.reset()
        self._sessions.clear()

    def __repr__(self) -> str:
        roles = [a.role.value for a in self.agents]
        return f"AdversarialCouncil(agents={len(self.agents)}, roles={roles})"
