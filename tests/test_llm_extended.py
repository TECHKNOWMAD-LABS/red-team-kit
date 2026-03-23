"""Extended tests for LLM client — covers sync/async complete, headers, payload building."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from redteamkit.llm import LLMClient, LLMConfig, LLMResponse


class TestLLMComplete:
    """Tests for synchronous complete() method."""

    def test_complete_success(self, llm_client, mock_httpx_response):
        mock_resp = mock_httpx_response(content="Critique result", model="gpt-4o")
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_resp
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=False)

        with patch("redteamkit.llm.httpx.Client", return_value=mock_client_instance):
            result = llm_client.complete([{"role": "user", "content": "test"}])

        assert isinstance(result, LLMResponse)
        assert result.content == "Critique result"
        mock_client_instance.post.assert_called_once()

    def test_complete_raises_on_http_error(self, llm_client):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_resp
        mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = MagicMock(return_value=False)

        with patch("redteamkit.llm.httpx.Client", return_value=mock_client_instance):
            with pytest.raises(httpx.HTTPStatusError):
                llm_client.complete([{"role": "user", "content": "test"}])


class TestLLMAsyncComplete:
    """Tests for async acomplete() method."""

    @pytest.mark.asyncio
    async def test_acomplete_success(self, llm_client, mock_httpx_response):
        mock_resp = mock_httpx_response(content="Async critique", model="gpt-4o")
        mock_resp.raise_for_status = MagicMock()

        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_resp
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)

        with patch("redteamkit.llm.httpx.AsyncClient", return_value=mock_async_client):
            result = await llm_client.acomplete([{"role": "user", "content": "test"}])

        assert isinstance(result, LLMResponse)
        assert result.content == "Async critique"


class TestLLMHelpers:
    """Tests for internal helper methods."""

    def test_build_headers_with_api_key(self, llm_client):
        headers = llm_client._build_headers()
        assert headers["Content-Type"] == "application/json"
        assert "Bearer test-key-000" in headers["Authorization"]

    def test_build_headers_without_api_key(self):
        config = LLMConfig(api_key="")
        client = LLMClient(config=config)
        headers = client._build_headers()
        assert "Authorization" not in headers

    def test_build_payload(self, llm_client):
        messages = [{"role": "user", "content": "hello"}]
        payload = llm_client._build_payload(messages)
        assert payload["model"] == "test-model"
        assert payload["messages"] == messages
        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 100

    def test_parse_response_empty_choices(self, llm_client):
        data = {"choices": [], "model": "m", "usage": {}}
        resp = llm_client._parse_response(data)
        assert resp.content == ""

    def test_parse_response_no_choices_key(self, llm_client):
        data = {"model": "m", "usage": {}}
        resp = llm_client._parse_response(data)
        assert resp.content == ""

    def test_generate_critique_prompt_without_context(self, llm_client):
        messages = llm_client.generate_critique_prompt(
            hypothesis="Test hypothesis",
            role="stress_tester",
        )
        assert len(messages) == 2
        assert "stress_tester" in messages[0]["content"]
        assert "Additional context" not in messages[1]["content"]
