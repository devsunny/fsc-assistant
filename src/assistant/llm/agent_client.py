"""Agent orchestrator facade backed by the unified runtime implementation."""
from __future__ import annotations

import logging
from typing import Any, Callable, Iterable, List, Optional, Union

from assistant.config.manager import AssistantConfig
from assistant.llm.runtime import (
    LLMConfigurationAdapter,
    OrchestrationParams,
    create_llm_runtime,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """High-level facade used by agents to interact with the LLM runtime."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        openai_client: Optional[Any] = None,
        stream_handler: Optional[Callable[[str], None]] = None,
        debug: bool = False,
        config: Optional[AssistantConfig] = None,
    ) -> None:
        self._config = config or AssistantConfig()
        self._base_url_override = base_url
        self._api_key_override = api_key
        self._client_override = openai_client
        self._stream_handler = stream_handler
        self._debug = debug
        self._runtime = None
        self._model_override: Optional[str] = None
        self._last_response_model: Optional[str] = None
        if self._debug:
            logger.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def runtime(self):
        if self._runtime is None:
            self._runtime = self._build_runtime()
        return self._runtime

    @property
    def client(self):
        return self.runtime.transport.client

    @property
    def model(self) -> str:
        return self._model_override or self.runtime.provider_config.primary_model

    @model.setter
    def model(self, value: str) -> None:
        self._model_override = value

    @property
    def chat_history(self):
        return self.runtime.history_manager

    @property
    def max_completion_tokens(self) -> int:
        return self.runtime.provider_config.max_completion_tokens

    @property
    def response_model(self) -> str:
        return self._last_response_model or self.model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def invoke_chat_stream(
        self,
        model: Optional[str] = None,
        inputs: Optional[List[dict]] = None,
        prompt: Optional[str] = None,
        tools: Optional[Iterable[Callable[..., Any]]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
    ) -> Union[str, List[dict]]:
        print("invoke_chat_stream called - tools = ", len(tools) if tools else 0)
        params = OrchestrationParams(
            model=model or self.model,
            messages=inputs,
            prompt=prompt,
            tools=tools,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            system_prompt=system_prompt,
            context=context,
            max_completion_tokens=max_completion_tokens,
            include_history=include_history,
            stream=True,
        )
        self._last_response_model = params.model
        result = self.runtime.orchestrator.invoke_stream(params)
        return result

    def invoke_chat(
        self,
        model: Optional[str] = None,
        inputs: Optional[List[dict]] = None,
        prompt: Optional[str] = None,
        tools: Optional[Iterable[Callable[..., Any]]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
    ) -> Union[str, List[dict]]:
        params = OrchestrationParams(
            model=model or self.model,
            messages=inputs,
            prompt=prompt,
            tools=tools,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            system_prompt=system_prompt,
            context=context,
            max_completion_tokens=max_completion_tokens,
            include_history=include_history,
            stream=False,
        )
        self._last_response_model = params.model
        result = self.runtime.orchestrator.invoke(params)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_runtime(self):
        history_path = self._config.get_option("llm", "chat_history_file", None)
        adapter = LLMConfigurationAdapter(self._config)
        runtime = create_llm_runtime(config_adapter=adapter, history_path=history_path)
        if self._client_override is not None:
            runtime.transport._client = self._client_override  # pylint: disable=protected-access
        client = runtime.transport.client
        if self._base_url_override:
            client.base_url = self._base_url_override
        if self._api_key_override:
            client.api_key = self._api_key_override
        runtime.orchestrator.configure_stream_handler(self._stream_handler)
        if self._model_override is None:
            self._model_override = runtime.provider_config.primary_model
        return runtime
