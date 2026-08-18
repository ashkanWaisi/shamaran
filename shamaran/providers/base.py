"""Provider contract kept independent from any LLM vendor."""

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ProviderResponse(BaseModel):
    content: str
    model: str | None = None
    raw: dict[str, Any] | None = None


class BaseProvider(ABC):
    name: str

    @abstractmethod
    def complete(
        self, messages: list[ChatMessage], tools: list[dict[str, Any]]
    ) -> ProviderResponse:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> tuple[bool, str]:
        raise NotImplementedError
