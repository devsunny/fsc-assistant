"""Configuration adapters for the unified LLM runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import httpx

from assistant.config.manager import AssistantConfig

DEFAULT_PROVIDER_KEY = "llm"
DEFAULT_MAX_COMPLETION_TOKENS = 150_000


@dataclass(frozen=True)
class TimeoutConfig:
    """Represents read/connect/write timeout configuration."""

    read: float
    connect: float
    write: float

    def as_httpx_timeout(self) -> httpx.Timeout:
        """Create an ``httpx.Timeout`` instance from the stored values."""
        return httpx.Timeout(
            self.read,
            connect=self.connect,
            read=self.read,
            write=self.write,
        )


@dataclass(frozen=True)
class LLMProviderConfig:
    """Normalized LLM provider configuration for transport clients."""

    provider_name: str
    provider_key: str
    base_url: Optional[str]
    api_key: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    models: List[str]
    max_completion_tokens: int
    timeout: TimeoutConfig

    @property
    def primary_model(self) -> str:
        """Return the first configured model."""
        return self.models[0]

    def iter_models(self, preferred: Optional[str] = None) -> Iterable[str]:
        """Yield configured models, optionally preferring a specific one first."""
        if preferred and preferred in self.models:
            yield preferred
        for model in self.models:
            if preferred and model == preferred:
                continue
            yield model

    def extra_headers(self) -> Dict[str, str]:
        """Return optional headers based on configured client credentials."""
        if not self.client_id or not self.client_secret:
            return {}
        return {
            "Client-Id": self.client_id,
            "Client-Secret": self.client_secret,
            "Application-Name": "Atlas-Phanes",
        }


class LLMConfigurationAdapter:
    """Loads and normalizes provider configuration for the LLM runtime."""

    def __init__(self, config: Optional[AssistantConfig] = None):
        self._config = config or AssistantConfig()

    @property
    def assistant_config(self) -> AssistantConfig:
        """Expose the underlying ``AssistantConfig`` instance."""
        return self._config

    def _provider_key(self, provider_name: str) -> str:
        return provider_name if provider_name != "default" else DEFAULT_PROVIDER_KEY

    def load_provider_config(self, provider_name: Optional[str] = None) -> LLMProviderConfig:
        """Build a ``LLMProviderConfig`` for the requested provider."""
        resolved_provider_name = (
            provider_name
            or self._config.get_option(DEFAULT_PROVIDER_KEY, "provider", default="default")
        )
        provider_key = self._provider_key(resolved_provider_name)

        base_url = self._config.get_option(provider_key, "base_url")
        api_key = self._config.get_option(provider_key, "api_key")
        client_id = self._config.get_option(provider_key, "client_id")
        client_secret = self._config.get_option(provider_key, "client_secret")
        models = self._normalize_models(provider_key)
        max_completion_tokens = self._config.get_int(
            provider_key, "max_completion_tokens", default=DEFAULT_MAX_COMPLETION_TOKENS
        )
        timeout = TimeoutConfig(
            read=self._config.get_float(DEFAULT_PROVIDER_KEY, "read_timeout", default=180.0),
            connect=self._config.get_float(DEFAULT_PROVIDER_KEY, "connect_timeout", default=5.0),
            write=self._config.get_float(DEFAULT_PROVIDER_KEY, "write_timeout", default=5.0),
        )

        self._validate_credentials(
            provider_name=resolved_provider_name,
            provider_key=provider_key,
            base_url=base_url,
            api_key=api_key,
            client_id=client_id,
            client_secret=client_secret,
        )

        return LLMProviderConfig(
            provider_name=resolved_provider_name,
            provider_key=provider_key,
            base_url=base_url,
            api_key=api_key,
            client_id=client_id,
            client_secret=client_secret,
            models=models,
            max_completion_tokens=max_completion_tokens,
            timeout=timeout,
        )

    def _normalize_models(self, provider_key: str) -> List[str]:
        models = self._config.get_option(provider_key, "models")
        assert models, f"please config LLM models in {AssistantConfig.CONFIG_FILENAME}"
        return [models] if isinstance(models, str) else list(models)

    def _validate_credentials(
        self,
        *,
        provider_name: str,
        provider_key: str,
        base_url: Optional[str],
        api_key: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> None:
        if provider_name == "openai":
            assert (
                api_key is not None
            ), f"please config LLM api_key in {AssistantConfig.CONFIG_FILENAME}"
            return

        if provider_name != "default":
            assert (
                base_url is not None
            ), f"please config LLM base url in {AssistantConfig.CONFIG_FILENAME}"

        if api_key:
            return

        assert (
            client_id is not None
        ), f"please config LLM client_id in {AssistantConfig.CONFIG_FILENAME}"
        assert (
            client_secret is not None
        ), f"please config LLM client_secret in {AssistantConfig.CONFIG_FILENAME}"
