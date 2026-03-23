"""Red team agent that challenges hypotheses from an assigned adversarial role."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Adversarial roles an agent can adopt during hypothesis evaluation."""

    DEVILS_ADVOCATE = "devils_advocate"
    CONTRARIAN = "contrarian"
    STRESS_TESTER = "stress_tester"
    ASSUMPTION_HUNTER = "assumption_hunter"
    BLIND_SPOT_FINDER = "blind_spot_finder"
    SCENARIO_EXPLORER = "scenario_explorer"


class Critique(BaseModel):
    """Structured output from an agent's evaluation of a hypothesis."""

    agent_id: str
    role: AgentRole
    hypothesis_id: str
    challenges: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RedTeamAgent:
    """An adversarial agent that evaluates hypotheses from a specific role."""

    def __init__(self, role: AgentRole, *, agent_id: str | None = None) -> None:
        self.agent_id = agent_id or uuid.uuid4().hex[:12]
        self.role = role
        self._critiques: list[Critique] = []

    @property
    def critiques(self) -> list[Critique]:
        """Return a copy of all critiques produced by this agent."""
        return list(self._critiques)

    def critique(
        self,
        hypothesis_id: str,
        challenges: list[str] | None = None,
        weaknesses: list[str] | None = None,
        counter_evidence: list[str] | None = None,
        confidence: float = 0.5,
        **metadata: Any,
    ) -> Critique:
        """Produce a critique of the given hypothesis."""
        if not hypothesis_id or not isinstance(hypothesis_id, str):
            raise ValueError("hypothesis_id must be a non-empty string")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {confidence}")
        result = Critique(
            agent_id=self.agent_id,
            role=self.role,
            hypothesis_id=hypothesis_id,
            challenges=challenges or [],
            weaknesses=weaknesses or [],
            counter_evidence=counter_evidence or [],
            confidence=confidence,
            metadata=metadata,
        )
        self._critiques.append(result)
        return result

    def reset(self) -> None:
        """Clear all stored critiques."""
        self._critiques.clear()

    def __repr__(self) -> str:
        return f"RedTeamAgent(role={self.role.value!r}, id={self.agent_id!r})"
