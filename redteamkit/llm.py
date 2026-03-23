"""LLM integration layer for generating adversarial critiques."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds


class LLMConfig(BaseModel):
    base_url: str = Field(default="https://api.openai.com/v1")
    api_key: str = Field(default="")
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    timeout: float = Field(default=30.0, gt=0)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        if not v.startswith(("https://", "http://")):
            raise ValueError("base_url must start with https:// or http://")
        return v.rstrip("/")

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

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        retries: int = MAX_RETRIES,
    ) -> LLMResponse:
        """Send a chat completion request synchronously with retry logic."""
        self._validate_messages(messages)
        headers = self._build_headers()
        payload = self._build_payload(messages)

        last_exc: Exception | None = None
        for attempt in range(retries):
            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.post(
                        f"{self.config.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                return self._parse_response(data)
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt < retries - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "LLM request failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt + 1, retries, exc, delay,
                    )
                    time.sleep(delay)
        raise last_exc  # type: ignore[misc]

    async def acomplete(
        self,
        messages: list[dict[str, str]],
        *,
        retries: int = MAX_RETRIES,
    ) -> LLMResponse:
        """Send a chat completion request asynchronously with retry logic."""
        self._validate_messages(messages)
        headers = self._build_headers()
        payload = self._build_payload(messages)

        last_exc: Exception | None = None
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                    resp = await client.post(
                        f"{self.config.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                return self._parse_response(data)
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt < retries - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "Async LLM request failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt + 1, retries, exc, delay,
                    )
                    await asyncio.sleep(delay)
        raise last_exc  # type: ignore[misc]

    @staticmethod
    def _validate_messages(messages: list[dict[str, str]]) -> None:
        """Validate message format before sending to API."""
        if not messages:
            raise ValueError("messages must be a non-empty list")
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise TypeError(f"messages[{i}] must be a dict, got {type(msg).__name__}")
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"messages[{i}] must have 'role' and 'content' keys")
            if not isinstance(msg["content"], str) or not msg["content"].strip():
                raise ValueError(f"messages[{i}]['content'] must be a non-empty string")

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
