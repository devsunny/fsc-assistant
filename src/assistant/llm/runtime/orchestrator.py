"""High-level orchestration that composes transport, history, and tools."""
from __future__ import annotations

import logging
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from assistant.llm.history import LLMChatHistoryManager
from assistant.llm.runtime.tools import ToolExecutionManager
from assistant.utils.cli.console import get_cli_console
from assistant.utils.llm.error_logger import log_error
from assistant.utils.llm.token_utils import count_message_tokens

from .config import LLMProviderConfig
from .transport import ChatRequest, ChatResponse, ChatStreamChunk, LLMTransportClient

logger = logging.getLogger(__name__)
MAX_INPUT_TOKENS = 64_000


@dataclass
class OrchestrationParams:
    """Parameters accepted by the orchestrator for a chat run."""

    model: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    prompt: Optional[str] = None
    tools: Optional[Iterable[Any]] = None
    temperature: float = 0.1
    reasoning_effort: Optional[str] = None
    system_prompt: Optional[str] = None
    context: Optional[dict] = None
    max_completion_tokens: Optional[int] = None
    include_history: Optional[int] = None
    stream: bool = False


class ChatOrchestrator:
    """Coordinates chat invocations across transport, history, and tool execution."""

    def __init__(
        self,
        *,
        provider_config: LLMProviderConfig,
        transport: LLMTransportClient,
        tool_manager: ToolExecutionManager,
        history_manager: LLMChatHistoryManager,
    ) -> None:
        self._provider_config = provider_config
        self._transport = transport
        self._history_manager = history_manager
        self._base_tool_manager = tool_manager
        self._tool_manager = tool_manager
        self._cli_console = get_cli_console()
        self._stream_handler: Optional[Any] = None

    @property
    def history(self) -> LLMChatHistoryManager:
        return self._history_manager

    @property
    def stream_handler(self):
        return self._stream_handler

    def configure_stream_handler(self, handler: Optional[Any]) -> None:
        self._stream_handler = handler
        self._tool_manager = self._base_tool_manager.with_stream_handler(handler)

    def invoke(self, params: OrchestrationParams) -> Any:
        """Invoke chat with optional tool loops (non-streaming)."""
        prepared = self._prepare(params)
        response = self._invoke_with_retry(prepared.request, prepared.original_messages)
        assistant_content, tool_calls = self._parse_non_stream_response(response.raw)
        self._history_manager.add_entry({"role": "assistant", "content": assistant_content})

        if not tool_calls:
            return assistant_content

        return self._handle_tool_loop(
            params=params,
            assistant_content=assistant_content,
            tool_calls=tool_calls,
            prepared=prepared,
        )

    def invoke_stream(self, params: OrchestrationParams) -> Any:
        """Invoke chat with streaming tokens and optional tool loops."""
        prepared = self._prepare(params)
        assistant_content, tool_calls = self._consume_stream(
            self._invoke_stream_with_retry(prepared.request, prepared.original_messages)
        )
        self._history_manager.add_entry({"role": "assistant", "content": assistant_content})

        if not tool_calls:
            return assistant_content

        return self._handle_tool_loop(
            params=params,
            assistant_content=assistant_content,
            tool_calls=tool_calls,
            prepared=prepared,
        )

    # ------------------------------------------------------------------
    # Preparation helpers
    # ------------------------------------------------------------------

    @dataclass
    class _PreparedRequest:
        request: ChatRequest
        original_messages: List[Dict[str, Any]]
        tools_mapping: Dict[str, Tuple[Any, bool]]
        tool_metadata: List[Dict[str, Any]]

    def _prepare(self, params: OrchestrationParams) -> "ChatOrchestrator._PreparedRequest":
        assert params.messages or params.prompt, "either messages or prompt is required"

        original_messages = (
            deepcopy(params.messages)
            if params.messages
            else [{"role": "user", "content": params.prompt}]
        )
        messages = deepcopy(original_messages)

        if params.include_history:
            messages = self._extend_history(messages, params.include_history)

        if params.system_prompt and (not messages or messages[0].get("role") != "system"):
            messages.insert(0, {"role": "system", "content": params.system_prompt})

        tool_metadata, tools_mapping = self._tool_manager.discover(params.tools)

        model = params.model or self._provider_config.primary_model
        temperature = 1 if model.startswith("gpt-5") else params.temperature
        request = ChatRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_completion_tokens=params.max_completion_tokens,
            reasoning_effort=params.reasoning_effort,
            tools=tool_metadata or None,
            stream=params.stream,
        )
        return ChatOrchestrator._PreparedRequest(
            request=request,
            original_messages=original_messages,
            tools_mapping=tools_mapping,
            tool_metadata=tool_metadata,
        )

    def _extend_history(
        self, messages: List[Dict[str, Any]], include_history: int
    ) -> List[Dict[str, Any]]:
        total_tokens = sum(count_message_tokens(msg, model=self._provider_config.primary_model) for msg in messages)
        history_messages = list(reversed(self._history_manager.get_chat_history(include_history)))
        fitted: List[Dict[str, Any]] = []
        for historic in history_messages:
            tokens = count_message_tokens(historic, model=self._provider_config.primary_model)
            if total_tokens + tokens > MAX_INPUT_TOKENS:
                break
            fitted.append(historic)
            total_tokens += tokens
        fitted.reverse()
        return fitted + messages

    # ------------------------------------------------------------------
    # Invocation helpers
    # ------------------------------------------------------------------

    def _invoke_with_retry(
        self, request: ChatRequest, original_messages: List[Dict[str, Any]]
    ) -> ChatResponse:
        try:
            return self._transport.execute_chat(request)
        except Exception as exc:  # pylint: disable=broad-except
            updated = self._adjust_request_on_error(request, exc)
            if updated is None:
                log_error(str(exc), **request.__dict__)
                raise
            return self._invoke_with_retry(updated, original_messages)
        finally:
            for msg in original_messages:
                self._history_manager.add_entry(msg)

    def _invoke_stream_with_retry(
        self, request: ChatRequest, original_messages: List[Dict[str, Any]]
    ) -> Iterable[ChatStreamChunk]:
        try:
            return self._transport.stream_chat(request)
        except Exception as exc:  # pylint: disable=broad-except
            updated = self._adjust_request_on_error(request, exc)
            if updated is None:
                log_error(str(exc), **request.__dict__)
                raise
            return self._invoke_stream_with_retry(updated, original_messages)
        finally:
            for msg in original_messages:
                self._history_manager.add_entry(msg)

    def _adjust_request_on_error(
        self, request: ChatRequest, exc: Exception
    ) -> Optional[ChatRequest]:
        message = str(exc)
        if "does not support parameters: ['tools']" in message:
            logger.warning("model does not support tools, retrying without tools")
            return ChatRequest(
                messages=self._clean_tool_calls(request.messages),
                model=request.model,
                temperature=request.temperature,
                max_completion_tokens=request.max_completion_tokens,
                reasoning_effort=request.reasoning_effort,
                tools=None,
                stream=request.stream,
            )
        if "The maximum tokens you requested exceeds the model limit of" in message:
            logger.warning("max tokens exceeded, clamping to provider limit")
            match = re.search(r"exceeds the model limit of (\d+)", message)
            if match:
                return ChatRequest(
                    messages=request.messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_completion_tokens=int(match.group(1)),
                    reasoning_effort=request.reasoning_effort,
                    tools=request.tools,
                    stream=request.stream,
                )
        if "Input is too long for requested model" in message:
            logger.warning("input too long, reducing messages")
            return ChatRequest(
                messages=self._reduce_messages(request.messages),
                model=request.model,
                temperature=request.temperature,
                max_completion_tokens=request.max_completion_tokens,
                reasoning_effort=request.reasoning_effort,
                tools=request.tools,
                stream=request.stream,
            )
        if "Only temperature=1 is supported" in message:
            logger.warning("forcing temperature to 1")
            return ChatRequest(
                messages=request.messages,
                model=request.model,
                temperature=1.0,
                max_completion_tokens=request.max_completion_tokens,
                reasoning_effort=request.reasoning_effort,
                tools=request.tools,
                stream=request.stream,
            )
        match = re.search(r"got an unexpected keyword argument '([\w_]+)'", message)
        if match:
            unexpected = match.group(1)
            logger.warning("removing unsupported parameter %s", unexpected)
            filtered_payload = {
                **request.__dict__,
                unexpected: None,
            }
            if unexpected == "tools":
                filtered_payload["messages"] = self._clean_tool_calls(request.messages)
            return ChatRequest(**{k: v for k, v in filtered_payload.items() if k != unexpected})
        return None

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _parse_non_stream_response(self, response: Any) -> Tuple[str, List[Tuple[str, str, str, str]]]:
        choice = response.choices[0]
        assistant_content = choice.message.content or ""
        tool_calls = []
        for call in getattr(choice.message, "tool_calls", []) or []:
            tool_calls.append((call.id, call.type, call.function.name, call.function.arguments))
        return assistant_content, tool_calls

    def _consume_stream(self, stream: Iterable[ChatStreamChunk]) -> Tuple[str, List[Tuple[str, str, str, str]]]:
        assistant_content = ""
        tool_calls: List[Tuple[str, str, str, str]] = []
        tool_index = -1
        tool_call_id = None
        tool_type = None
        tool_name = None
        tool_args_json = ""
        shown_model = None

        for chunk_wrapper in stream:
            chunk = chunk_wrapper.raw
            if getattr(chunk, "model", None) and self._stream_handler and shown_model is None:
                self._cli_console.print(
                    f"\n[Assistant - {chunk.model}]",
                    color="green",
                    end=" ",
                )
                shown_model = chunk.model

            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            if getattr(delta, "content", None):
                if self._stream_handler:
                    self._stream_handler(delta.content)
                assistant_content += delta.content

            tool_deltas = getattr(delta, "tool_calls", None)
            if tool_deltas:
                if self._stream_handler:
                    self._stream_handler("\n")
                call = tool_deltas[0]
                index = call.index
                if call.id and call.function and index != tool_index:
                    if tool_call_id and tool_name:
                        tool_calls.append((tool_call_id, tool_type, tool_name, tool_args_json))
                        tool_call_id = None
                        tool_name = None
                        tool_type = None
                        tool_args_json = ""
                    tool_name = call.function.name
                    tool_call_id = call.id
                    tool_type = call.type
                    tool_args_json = call.function.arguments
                    tool_index = index
                    if self._stream_handler:
                        self._stream_handler(f"tool_name:{tool_name}\n")
                        self._stream_handler(f"tool_id:{tool_call_id}\n")
                elif call.function:
                    if self._stream_handler:
                        self._stream_handler(call.function.arguments)
                    tool_args_json += call.function.arguments

            if chunk.choices[0].finish_reason == "tool_calls" and tool_call_id and tool_name:
                tool_calls.append((tool_call_id, tool_type, tool_name, tool_args_json))

        if self._stream_handler:
            self._stream_handler("\n")

        return assistant_content, tool_calls

    # ------------------------------------------------------------------
    # Tool handling helpers
    # ------------------------------------------------------------------

    def _handle_tool_loop(
        self,
        *,
        params: OrchestrationParams,
        assistant_content: str,
        tool_calls: List[Tuple[str, str, str, str]],
        prepared: "ChatOrchestrator._PreparedRequest",
    ) -> Any:
        calls: List[Dict[str, Any]] = []
        results: List[Dict[str, Any]] = []
        for tool_call_id, tool_type, tool_name, tool_args_json in tool_calls:
            if tool_name not in prepared.tools_mapping:
                logger.warning("No tool mapping found for %s", tool_name)
                continue
            func, stateless = prepared.tools_mapping[tool_name]
            context = params.context if not stateless else None
            tool_messages = self._tool_manager.execute(
                tool=func,
                assistant_content=assistant_content,
                tool_call_id=tool_call_id,
                tool_type=tool_type,
                tool_name=tool_name,
                tool_json_args=tool_args_json,
                context=context,
            )
            calls.append(tool_messages[0])
            results.append(tool_messages[1])

        if not calls:
            return assistant_content

        follow_up_params = OrchestrationParams(
            model=params.model,
            messages=[
                {
                    "role": "assistant",
                    "content": assistant_content,
                    "tool_calls": calls,
                },
                *results,
            ],
            tools=params.tools,
            temperature=params.temperature,
            reasoning_effort=params.reasoning_effort,
            system_prompt=params.system_prompt,
            context=params.context,
            max_completion_tokens=params.max_completion_tokens,
            include_history=params.include_history,
            stream=params.stream,
        )

        return self.invoke_stream(follow_up_params) if params.stream else self.invoke(
            follow_up_params
        )

    # ------------------------------------------------------------------
    # Message cleanup helpers
    # ------------------------------------------------------------------

    def _clean_tool_calls(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for msg in messages:
            if msg.get("role") == "tool" or "tool_calls" in msg:
                continue
            cleaned.append(msg)
        return cleaned

    def _reduce_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not messages:
            raise ValueError("messages are required")
        has_system = messages[0].get("role") == "system"
        trimmed: List[Dict[str, Any]] = []
        tail = messages[1:] if has_system else messages
        if has_system:
            trimmed.append(messages[0])
        if len(tail) == 1:
            raise ValueError("input text exceeded input token limit")
        half = len(tail) // 2
        for offset in range(half + 1):
            candidate = tail[half - offset]
            if candidate.get("role") in {"user", "assistant"}:
                half = half - offset
                break
        trimmed.extend(tail[half:])
        return trimmed
