"""Tests for the unified LLM chat orchestrator runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional

from assistant.llm.history import LLMChatHistoryManager
from assistant.llm.runtime.config import LLMProviderConfig, TimeoutConfig
from assistant.llm.runtime.orchestrator import ChatOrchestrator, OrchestrationParams
from assistant.llm.runtime.tools import ToolExecutionManager
from assistant.llm.runtime.transport import ChatResponse, ChatStreamChunk


@dataclass
class _FakeFunction:
    name: str
    arguments: str


@dataclass
class _FakeToolCall:
    id: str
    type: str
    function: _FakeFunction
    index: int = 0


@dataclass
class _FakeMessage:
    content: Optional[str] = None
    tool_calls: Optional[List[_FakeToolCall]] = None


@dataclass
class _FakeChoice:
    message: _FakeMessage
    finish_reason: Optional[str] = "stop"


@dataclass
class _FakeResponse:
    choices: List[_FakeChoice]
    model: str = "stub-model"


@dataclass
class _FakeDelta:
    content: Optional[str] = None
    tool_calls: Optional[List[_FakeToolCall]] = None


@dataclass
class _FakeChunkChoice:
    delta: Optional[_FakeDelta]
    finish_reason: Optional[str] = None


@dataclass
class _FakeStreamChunk:
    model: str
    choices: List[_FakeChunkChoice]


class _FakeTransport:
    def __init__(
        self,
        provider_config: LLMProviderConfig,
        responses: Optional[Iterable[_FakeResponse]] = None,
        streams: Optional[Iterable[Iterable[_FakeStreamChunk]]] = None,
    ) -> None:
        self._provider_config = provider_config
        self._responses = list(responses or [])
        self._streams = [list(stream) for stream in (streams or [])]
        self.request_history: List[Any] = []

    def execute_chat(self, request):
        self.request_history.append(("chat", request))
        response = self._responses.pop(0)
        return ChatResponse(raw=response)

    def stream_chat(self, request):
        self.request_history.append(("stream", request))
        chunks = self._streams.pop(0)
        for chunk in chunks:
            yield ChatStreamChunk(raw=chunk)

    def available_models(self, preferred: Optional[str] = None):
        return self._provider_config.iter_models(preferred)


def _build_orchestrator(
    tmp_path,
    *,
    responses: Optional[List[_FakeResponse]] = None,
    streams: Optional[List[List[_FakeStreamChunk]]] = None,
):
    provider_config = LLMProviderConfig(
        provider_name="stub",
        provider_key="stub",
        base_url=None,
        api_key="key",
        client_id=None,
        client_secret=None,
        models=["stub-model"],
        max_completion_tokens=1024,
        timeout=TimeoutConfig(read=1.0, connect=1.0, write=1.0),
    )
    history_file = tmp_path / "history.json"
    history_manager = LLMChatHistoryManager(history_file_path=history_file)
    tool_manager = ToolExecutionManager()
    transport = _FakeTransport(
        provider_config=provider_config,
        responses=responses,
        streams=streams,
    )
    orchestrator = ChatOrchestrator(
        provider_config=provider_config,
        transport=transport,
        tool_manager=tool_manager,
        history_manager=history_manager,
    )
    return orchestrator, transport, history_manager


def test_invoke_chat_returns_assistant_response(tmp_path):
    response = _FakeResponse(
        choices=[_FakeChoice(message=_FakeMessage(content="hello from model"))]
    )
    orchestrator, transport, history = _build_orchestrator(
        tmp_path, responses=[response]
    )

    result = orchestrator.invoke(OrchestrationParams(prompt="hello"))

    assert result == "hello from model"
    assert transport.request_history and transport.request_history[0][0] == "chat"
    assert history.get_history_count() >= 1


def test_invoke_chat_stream_aggregates_tokens(tmp_path):
    stream_chunks = [
        _FakeStreamChunk(
            model="stub-model",
            choices=[_FakeChunkChoice(delta=_FakeDelta(content="hi "))],
        ),
        _FakeStreamChunk(
            model="stub-model",
            choices=[
                _FakeChunkChoice(
                    delta=_FakeDelta(content="there"),
                    finish_reason="stop",
                )
            ],
        ),
    ]
    orchestrator, transport, _ = _build_orchestrator(
        tmp_path, streams=[stream_chunks]
    )
    streamed_tokens: List[str] = []
    orchestrator.configure_stream_handler(streamed_tokens.append)

    result = orchestrator.invoke_stream(OrchestrationParams(prompt="hi", stream=True))

    assert result == "hi there"
    assert "".join(streamed_tokens).replace("\n", "") == "hi there"
    assert transport.request_history and transport.request_history[0][0] == "stream"


def test_tool_invocation_executes_and_retries_request(tmp_path):
    tool_call = _FakeToolCall(
        id="call-1",
        type="function",
        function=_FakeFunction(name="echo_tool", arguments='{"text": "ping"}'),
    )
    first_response = _FakeResponse(
        choices=[
            _FakeChoice(
                message=_FakeMessage(content="", tool_calls=[tool_call]),
                finish_reason="tool_calls",
            )
        ]
    )
    second_response = _FakeResponse(
        choices=[_FakeChoice(message=_FakeMessage(content="pong"))]
    )
    orchestrator, transport, _ = _build_orchestrator(
        tmp_path, responses=[first_response, second_response]
    )

    def echo_tool(text: str):
        return {"content": text + " processed"}

    result = orchestrator.invoke(
        OrchestrationParams(
            prompt="ping",
            tools=[echo_tool],
        )
    )

    assert result == "pong"
    # Two execute_chat calls: initial request and follow-up after tool run
    assert len([kind for kind, _ in transport.request_history if kind == "chat"]) == 2