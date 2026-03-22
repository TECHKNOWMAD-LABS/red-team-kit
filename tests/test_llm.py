"""Tests for the LLM client module."""

from redteamkit.llm import LLMClient, LLMConfig, LLMResponse


def test_llm_config_defaults():
    config = LLMConfig()
    assert config.model == "gpt-4o"
    assert config.temperature == 0.7
    assert config.max_tokens == 2048


def test_llm_config_from_env(monkeypatch):
    monkeypatch.setenv("REDTEAM_LLM_MODEL", "claude-sonnet-4-6")
    monkeypatch.setenv("REDTEAM_LLM_BASE_URL", "https://api.anthropic.com/v1")
    config = LLMConfig.from_env()
    assert config.model == "claude-sonnet-4-6"
    assert "anthropic" in config.base_url


def test_llm_generate_critique_prompt():
    client = LLMClient(config=LLMConfig())
    messages = client.generate_critique_prompt(
        hypothesis="Revenue will double next quarter",
        role="contrarian",
        context="Early-stage startup",
    )
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "contrarian" in messages[0]["content"]
    assert "Revenue" in messages[1]["content"]


def test_llm_parse_response():
    client = LLMClient(config=LLMConfig())
    data = {
        "choices": [{"message": {"content": "This hypothesis is flawed"}}],
        "model": "test-model",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
    }
    response = client._parse_response(data)
    assert isinstance(response, LLMResponse)
    assert response.content == "This hypothesis is flawed"
    assert response.model == "test-model"
