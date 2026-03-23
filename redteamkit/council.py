"""Adversarial council that orchestrates red-team agents to stress-test hypotheses."""

from __future__ import annotations

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
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
        if not hypothesis_id or not isinstance(hypothesis_id, str):
            raise ValueError("hypothesis_id must be a non-empty string")
        if not self.agents:
            raise ValueError("Council has no agents — add agents before running a session")
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

    async def arun_session(
        self,
        hypothesis_id: str,
        challenges_per_agent: list[str] | None = None,
        weaknesses_per_agent: list[str] | None = None,
        confidence: float = 0.5,
        *,
        max_concurrency: int = 10,
    ) -> SessionRecord:
        """Run an adversarial session with agents critiquing in parallel."""
        if not hypothesis_id or not isinstance(hypothesis_id, str):
            raise ValueError("hypothesis_id must be a non-empty string")
        if not self.agents:
            raise ValueError("Council has no agents — add agents before running a session")

        semaphore = asyncio.Semaphore(max_concurrency)
        session_id = uuid.uuid4().hex[:12]

        async def _critique(agent: RedTeamAgent) -> Critique:
            async with semaphore:
                return agent.critique(
                    hypothesis_id=hypothesis_id,
                    challenges=challenges_per_agent or [f"Challenge from {agent.role.value}"],
                    weaknesses=weaknesses_per_agent,
                    confidence=confidence,
                )

        critiques = await asyncio.gather(*[_critique(a) for a in self.agents])

        score = self.scorer.score(hypothesis_id, list(critiques))
        record = SessionRecord(
            session_id=session_id,
            hypothesis_id=hypothesis_id,
            critiques=list(critiques),
            score=score,
        )
        self._sessions.append(record)
        return record

    def run_batch(
        self,
        hypothesis_ids: list[str],
        confidence: float = 0.5,
        *,
        max_workers: int = 4,
    ) -> list[SessionRecord]:
        """Run sessions for multiple hypotheses in parallel using threads."""
        if not hypothesis_ids:
            raise ValueError("hypothesis_ids must be a non-empty list")

        def _run_one(h_id: str) -> SessionRecord:
            return self.run_session(h_id, confidence=confidence)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(_run_one, hypothesis_ids))
        return results

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
