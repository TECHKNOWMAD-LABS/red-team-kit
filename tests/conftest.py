"""Shared fixtures and mock helpers for red-team-kit tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from redteamkit.agent import AgentRole, Critique, RedTeamAgent
from redteamkit.council import AdversarialCouncil
from redteamkit.llm import LLMClient, LLMConfig
from redteamkit.scoring import HypothesisScorer


@pytest.fixture
def sample_config():
    """LLM config with test defaults (no real API calls)."""
    return LLMConfig(
        base_url="https://test.local/v1",
        api_key="test-key-000",
        model="test-model",
        temperature=0.5,
        max_tokens=100,
        timeout=5.0,
    )


@pytest.fixture
def llm_client(sample_config):
    """LLM client with test config."""
    return LLMClient(config=sample_config)


@pytest.fixture
def mock_httpx_response():
    """Factory for mock httpx responses."""
    def _make(content="Test response", model="test-model", status_code=200):
        data = {
            "choices": [{"message": {"content": content}}],
            "model": model,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = data
        resp.raise_for_status = MagicMock()
        return resp
    return _make


@pytest.fixture
def sample_critiques():
    """A list of sample critiques for scoring tests."""
    return [
        Critique(
            agent_id="agent-1",
            role=AgentRole.DEVILS_ADVOCATE,
            hypothesis_id="H-TEST",
            challenges=["Challenge 1", "Challenge 2"],
            weaknesses=["Weakness 1"],
            counter_evidence=["Counter 1"],
            confidence=0.6,
        ),
        Critique(
            agent_id="agent-2",
            role=AgentRole.CONTRARIAN,
            hypothesis_id="H-TEST",
            challenges=["Challenge 3"],
            weaknesses=["Weakness 2", "Weakness 3"],
            counter_evidence=[],
            confidence=0.4,
        ),
    ]


@pytest.fixture
def council_two_agents():
    """A council with two agents for quick tests."""
    return AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])


@pytest.fixture
def scorer():
    """Default hypothesis scorer."""
    return HypothesisScorer()
