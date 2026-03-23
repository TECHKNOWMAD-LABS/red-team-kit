"""Tests for input validation and error handling across all modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from redteamkit.agent import AgentRole, RedTeamAgent
from redteamkit.council import AdversarialCouncil
from redteamkit.llm import LLMClient, LLMConfig


class TestAgentValidation:
    """Input validation on RedTeamAgent.critique()."""

    def test_empty_hypothesis_id(self):
        agent = RedTeamAgent(role=AgentRole.CONTRARIAN)
        with pytest.raises(ValueError, match="hypothesis_id"):
            agent.critique(hypothesis_id="")

    def test_none_hypothesis_id(self):
        agent = RedTeamAgent(role=AgentRole.CONTRARIAN)
        with pytest.raises(ValueError, match="hypothesis_id"):
            agent.critique(hypothesis_id=None)  # type: ignore[arg-type]

    def test_confidence_too_high(self):
        agent = RedTeamAgent(role=AgentRole.CONTRARIAN)
        with pytest.raises(ValueError, match="confidence"):
            agent.critique(hypothesis_id="H-001", confidence=1.5)

    def test_confidence_negative(self):
        agent = RedTeamAgent(role=AgentRole.CONTRARIAN)
        with pytest.raises(ValueError, match="confidence"):
            agent.critique(hypothesis_id="H-001", confidence=-0.1)


class TestCouncilValidation:
    """Input validation on AdversarialCouncil.run_session()."""

    def test_empty_hypothesis_id(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        with pytest.raises(ValueError, match="hypothesis_id"):
            council.run_session("")

    def test_no_agents(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        council.agents.clear()
        with pytest.raises(ValueError, match="no agents"):
            council.run_session("H-001")


class TestLLMValidation:
    """Input validation on LLMClient methods."""

    def test_empty_messages(self):
        client = LLMClient(config=LLMConfig())
        with pytest.raises(ValueError, match="non-empty"):
            client.complete([])

    def test_message_missing_role(self):
        client = LLMClient(config=LLMConfig())
        with pytest.raises(ValueError, match="'role' and 'content'"):
            client.complete([{"content": "hello"}])

    def test_message_empty_content(self):
        client = LLMClient(config=LLMConfig())
        with pytest.raises(ValueError, match="non-empty string"):
            client.complete([{"role": "user", "content": ""}])

    def test_message_whitespace_content(self):
        client = LLMClient(config=LLMConfig())
        with pytest.raises(ValueError, match="non-empty string"):
            client.complete([{"role": "user", "content": "   "}])

    def test_message_not_dict(self):
        client = LLMClient(config=LLMConfig())
        with pytest.raises(TypeError, match="must be a dict"):
            client.complete(["not a dict"])  # type: ignore[list-item]


class TestLLMRetry:
    """Retry logic in LLMClient.complete()."""

    def test_retries_on_timeout(self):
        client = LLMClient(config=LLMConfig(timeout=0.1))
        mock_client_instance = MagicMock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("timeout")
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=False)

        with patch("redteamkit.llm.httpx.Client", return_value=mock_client_instance):
            with patch("redteamkit.llm.time.sleep"):  # skip actual delays
                with pytest.raises(httpx.TimeoutException):
                    client.complete(
                        [{"role": "user", "content": "test"}],
                        retries=2,
                    )
        assert mock_client_instance.post.call_count == 2

    def test_succeeds_after_retry(self, mock_httpx_response):
        client = LLMClient(config=LLMConfig(timeout=1.0))
        good_resp = mock_httpx_response(content="OK")

        mock_client_instance = MagicMock()
        mock_client_instance.post.side_effect = [
            httpx.ConnectError("connect failed"),
            good_resp,
        ]
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=False)

        with patch("redteamkit.llm.httpx.Client", return_value=mock_client_instance):
            with patch("redteamkit.llm.time.sleep"):
                result = client.complete(
                    [{"role": "user", "content": "test"}],
                    retries=3,
                )
        assert result.content == "OK"
        assert mock_client_instance.post.call_count == 2
