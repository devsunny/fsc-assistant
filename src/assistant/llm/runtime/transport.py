"""Transport helpers that encapsulate SDK interactions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional

from .config import LLMProviderConfig


@dataclass
class ChatRequest:
    """Normalized parameters for a chat completion request."""

    messages: List[Dict[str, Any]]
    model: str
    temperature: float = 0.1
    max_completion_tokens: Optional[int] = None
    reasoning_effort: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Dict[str, Any]] = None
    stream: bool = False


@dataclass
class ChatResponse:
    """Wrapper around the provider response object."""

    raw: Any


@dataclass
class ChatStreamChunk:
    """Wrapper for streaming response chunks."""

    raw: Any


class LLMTransportClient:
    """Handles construction of SDK clients and execution of chat requests."""

    def __init__(self, provider_config: LLMProviderConfig):
        self._provider_config = provider_config
        self._client = None
        self._openai_module = None

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client

        if self._openai_module is None:
            import openai

            self._openai_module = openai

        client_kwargs: Dict[str, Any] = {
            "api_key": self._provider_config.api_key,
            "timeout": self._provider_config.timeout.as_httpx_timeout(),
        }
        if self._provider_config.base_url:
            client_kwargs["base_url"] = self._provider_config.base_url

        extra_headers = self._provider_config.extra_headers()
        if extra_headers:
            from getpass import getuser

            client_kwargs["default_headers"] = {
                **extra_headers,
                "Username": getuser(),
            }

        self._client = self._openai_module.OpenAI(**client_kwargs)
        return self._client

    @property
    def client(self) -> Any:
        """Expose the lazily created OpenAI client."""
        return self._ensure_client()

    def available_models(self, preferred: Optional[str] = None) -> Iterable[str]:
        """Yield configured models, preferring the requested one if present."""
        return self._provider_config.iter_models(preferred)

    def execute_chat(self, request: ChatRequest) -> ChatResponse:
        """Execute a non-streaming chat completion."""
        payload = self._build_payload(request)
        response = self.client.chat.completions.create(**payload)
        return ChatResponse(raw=response)

    def stream_chat(self, request: ChatRequest) -> Iterator[ChatStreamChunk]:
        """Execute a streaming chat completion."""
        payload = self._build_payload(request)
        payload["stream"] = True
        stream = self.client.chat.completions.create(**payload)
        for chunk in stream:
            yield ChatStreamChunk(raw=chunk)

    def _build_payload(self, request: ChatRequest) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
        }
        if request.max_completion_tokens is not None:
            payload["max_tokens"] = min(
                request.max_completion_tokens, self._provider_config.max_completion_tokens
            )
        if request.reasoning_effort:
            payload["reasoning_effort"] = request.reasoning_effort
        if request.tools:
            payload["tools"] = request.tools
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice
        return payload
