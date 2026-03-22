"""LLM integration layer for generating adversarial critiques."""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    base_url: str = Field(default="https://api.openai.com/v1")
    api_key: str = Field(default="")
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    timeout: float = Field(default=30.0, gt=0)

    @classmethod
    def from_env(cls) -> LLMConfig:
        return cls(
            base_url=os.environ.get("REDTEAM_LLM_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("REDTEAM_LLM_API_KEY", ""),
            model=os.environ.get("REDTEAM_LLM_MODEL", "gpt-4o"),
        )


class LLMResponse(BaseModel):
    content: str
    model: str = ""
    usage: dict[str, int] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class LLMClient:
    """Async-capable HTTP client for LLM API calls."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig.from_env()

    def complete(self, messages: list[dict[str, str]]) -> LLMResponse:
        """Send a chat completion request synchronously."""
        headers = self._build_headers()
        payload = self._build_payload(messages)

        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        return self._parse_response(data)

    async def acomplete(self, messages: list[dict[str, str]]) -> LLMResponse:
        """Send a chat completion request asynchronously."""
        headers = self._build_headers()
        payload = self._build_payload(messages)

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        return self._parse_response(data)

    def generate_critique_prompt(
        self, hypothesis: str, role: str, context: str = ""
    ) -> list[dict[str, str]]:
        """Build a prompt for an adversarial critique of a hypothesis."""
        system_msg = (
            f"You are a {role} analyst on a red team. "
            "Your job is to find weaknesses, hidden assumptions, and counter-evidence "
            "in the hypothesis presented. Be rigorous and specific."
        )
        user_msg = f"Hypothesis: {hypothesis}"
        if context:
            user_msg += f"\n\nAdditional context: {context}"
        user_msg += (
            "\n\nProvide your critique as:\n"
            "1. Key challenges to this hypothesis\n"
            "2. Hidden weaknesses or assumptions\n"
            "3. Counter-evidence or scenarios where this fails\n"
            "4. Your confidence level (0-1) that this hypothesis is flawed"
        )
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _build_payload(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

    def _parse_response(self, data: dict[str, Any]) -> LLMResponse:
        content = ""
        if data.get("choices"):
            content = data["choices"][0].get("message", {}).get("content", "")
        return LLMResponse(
            content=content,
            model=data.get("model", ""),
            usage=data.get("usage", {}),
            raw=data,
        )
