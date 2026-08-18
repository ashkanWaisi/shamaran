"""Provider for OpenAI-compatible local and hosted model servers."""

from typing import Any

import httpx

from shamaran.exceptions import ConfigurationError, ProviderError

from .base import BaseProvider, ChatMessage, ProviderResponse


class OpenAICompatibleProvider(BaseProvider):
    name = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = client or httpx.Client(timeout=timeout, headers=headers)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self.client.request(method, f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as exc:
            raise ProviderError(
                f"Model server timed out after {self.timeout:g} seconds. Endpoint: {self.base_url}"
            ) from exc
        except httpx.ConnectError as exc:
            raise ProviderError(
                f"Shamaran could not connect to the model server at {self.base_url}."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise ProviderError(
                f"Model server returned HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Model server request failed: {exc}") from exc

    @staticmethod
    def _messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
        converted: list[dict[str, str]] = []
        for message in messages:
            if message.role == "tool":
                converted.append({"role": "user", "content": f"Tool observation:\n{message.content}"})
            else:
                converted.append({"role": message.role, "content": message.content})
        return converted

    def complete(
        self, messages: list[ChatMessage], tools: list[dict[str, Any]]
    ) -> ProviderResponse:
        if not self.model:
            raise ConfigurationError("Select a model from the connected model server.")
        response = self._request(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,
                "messages": self._messages(messages),
                "temperature": 0,
                "stream": False,
            },
        )
        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("message content is not text")
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Model server returned a malformed chat response.") from exc
        return ProviderResponse(content=content, model=payload.get("model"), raw=payload)

    def models(self) -> list[str]:
        response = self._request("GET", "/models")
        try:
            return [item["id"] for item in response.json().get("data", []) if item.get("id")]
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            raise ProviderError("Model server returned malformed model data.") from exc

    def health(self) -> tuple[bool, str]:
        try:
            models = self.models()
        except ProviderError as exc:
            return False, str(exc)
        if self.model and self.model not in models:
            return False, f"Configured model is unavailable: {self.model}"
        return True, f"Model server reachable; {len(models)} model(s) available"
