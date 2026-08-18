"""Factories for configured providers."""

from collections.abc import Callable

from shamaran.config import Settings
from shamaran.exceptions import ConfigurationError

from .base import BaseProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider


ProviderFactory = Callable[[Settings], BaseProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}

    def register(self, name: str, factory: ProviderFactory) -> None:
        self._factories[name.lower()] = factory

    def create(self, settings: Settings) -> BaseProvider:
        try:
            return self._factories[settings.provider](settings)
        except KeyError as exc:
            available = ", ".join(sorted(self._factories))
            raise ConfigurationError(
                f"Unknown provider '{settings.provider}'. Available: {available}"
            ) from exc


def default_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(
        "ollama",
        lambda settings: OllamaProvider(
            settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout
        ),
    )
    registry.register(
        "openai-compatible",
        lambda settings: OpenAICompatibleProvider(
            settings.compatible_base_url,
            settings.compatible_model,
            settings.compatible_api_key,
            settings.compatible_timeout,
        ),
    )
    return registry
