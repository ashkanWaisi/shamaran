"""Ollama chat API provider with concise error translation."""

import json
from typing import Any

import httpx

from shamaran.exceptions import ConfigurationError, ProviderError

from .base import BaseProvider, ChatMessage, ProviderResponse


AGENT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "plan": {"type": "array", "items": {"type": "string"}},
        "action": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "arguments": {"type": "object"},
            },
            "required": ["tool", "arguments"],
            "additionalProperties": False,
        },
        "final": {"type": "string"},
    },
    "additionalProperties": False,
}


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.client = client or httpx.Client(timeout=timeout)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self.client.request(method, f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"Ollama request timed out after {self.timeout:g} seconds.\nEndpoint: {self.base_url}"
            ) from exc
        except httpx.ConnectError as exc:
            raise ProviderError(
                "Shamaran could not connect to Ollama.\n\n"
                f"Configured endpoint:\n{self.base_url}\n\n"
                "Check that Ollama is installed and running."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise ProviderError(
                f"Ollama returned HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc

    def complete(
        self, messages: list[ChatMessage], tools: list[dict[str, Any]]
    ) -> ProviderResponse:
        if not self.model or self.model == "YOUR_MODEL_NAME":
            raise ConfigurationError("Set OLLAMA_MODEL in .env to an installed model.")
        response = self._request(
            "POST",
            "/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "format": AGENT_RESPONSE_SCHEMA,
                "messages": [message.model_dump() for message in messages],
                "options": {"temperature": 0},
            },
        )
        try:
            payload = response.json()
            content = payload["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("message.content is not text")
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderError("Ollama returned a malformed chat response.") from exc
        return ProviderResponse(content=content, model=payload.get("model"), raw=payload)

    def models(self) -> list[str]:
        response = self._request("GET", "/api/tags")
        try:
            payload = response.json()
            return [item["name"] for item in payload.get("models", []) if "name" in item]
        except (ValueError, TypeError) as exc:
            raise ProviderError("Ollama returned malformed model data.") from exc

    def health(self) -> tuple[bool, str]:
        try:
            models = self.models()
        except ProviderError as exc:
            return False, str(exc)
        if not self.model or self.model == "YOUR_MODEL_NAME":
            return False, "OLLAMA_MODEL is not configured"
        if self.model not in models:
            return False, f"Configured model is unavailable: {self.model}"
        return True, f"Ollama reachable; model {self.model} is available"
