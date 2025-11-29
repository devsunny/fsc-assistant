## Context
The current LLM client functionality is split across two modules (`client.py` and `agent_client.py`). Each module owns overlapping configuration, request preparation, and tool-coordination logic, resulting in duplicated state handling and code paths that are hard to extend for new LLM providers. The orchestrator internally instantiates `LLMClient`, but both modules surface public classes that downstream code imports directly. This tight coupling makes it difficult to introduce new orchestration strategies or swap transport layers without touching high-level orchestration code.

## Current Responsibilities
- **`LLMClient`**
  - Loads provider configuration (base URL, credentials, model roster, timeouts) via `AssistantConfig` and enforces required settings.
  - Builds `OpenAI` SDK clients on demand, including optional client credential headers, and exposes the raw client through `native_client`.
  - Calculates granular `httpx.Timeout` instances and exposes helper APIs for non-streaming, streaming, and generator-based chat completions.
  - Enforces request limits (max completion tokens, per-model fallbacks) and logs provider errors before yielding responses.
  - Provides a module-level singleton `llmclient` that downstream code can import directly for quick access.
- **`AgentOrchestrator`**
  - Lazily instantiates `LLMClient`, the underlying `OpenAI` client, retry decorators, and heavy dependencies to keep CLI startup fast.
  - Tracks chat history through `LLMChatHistoryManager`, managing history truncation by token budget and persisting conversation state.
  - Orchestrates tool discovery, execution, and looping, delegating to `ToolExecutionHandler` while deduplicating repeated tool calls.
  - Normalizes chat parameters for streaming and non-streaming invocations, including system prompt injection, reasoning effort, and model overrides.
  - Handles provider error adaptation (unsupported arguments, token limits, temperature constraints) and retries with adjusted parameters before surfacing failures.

## Known Consumers
- **CLI/agent entry points**: `src/assistant/agents/shell.py` lazily constructs `AgentOrchestrator` for interactive sessions; `src/assistant/llm/utils.py` and `src/assistant/llm/__init__.py` re-export `LLMClient` helpers.
- **Global helpers**: `src/assistant/llm/client.py` exposes `llmclient` module singleton; callers can use `assistant.llm.create_llm_client()` for new instances.
- **Documentation and specs**: `docs/refactor-agent-client.md` and legacy OpenSpec changes reference current class shapes, highlighting areas that must remain backwards compatible.
- **Cross-language artifacts**: `nodejs-version/__tests__` and `nodejs-version/test-all.js` import a parallel `LLMClient` wrapper, indicating tooling parity expectations when restructuring exports.

## Target Architecture Overview
- **Configuration Layer (`LLMConfigurationAdapter`)**
  - Responsible for reading `AssistantConfig`, normalizing provider options, and exposing immutable configuration objects per provider/model set.
  - Supplies validated connection details (base URL, credentials, model catalog, token budgets, timeout settings) to downstream collaborators.
- **Transport Layer (`LLMTransportClient`)**
  - Owns construction and caching of SDK/native clients (OpenAI or provider-specific) using configuration data.
  - Centralizes retry/backoff policies, timeout wiring, and low-level request execution primitives shared across streaming and non-streaming flows.
- **Orchestration Layer (`ChatOrchestrator`)**
  - Coordinates message preparation, history augmentation, and response handling while remaining agnostic to concrete transport specifics.
  - Delegates history management to injected `ChatHistoryStore` implementations and tool execution to the tool layer.
- **Tool Layer (`ToolExecutionManager`)**
  - Discovers available tools, executes tool calls, deduplicates repeated invocations, and serializes tool responses.
- **Facades / Compatibility Shims**
  - `LLMClient` and `AgentOrchestrator` remain as thin facades that compose the new collaborators, preserving public APIs and acting as the migration surface.

## Interfaces and Boundaries
- **`LLMConfigurationAdapter`**
  - `load()` → returns provider configuration dataclass (base URL, credentials, model list, max tokens, timeout policy).
  - `select_model(preferred: Optional[str])` → resolves an available model identifier.
- **`LLMTransportClient`**
  - `create_session()` → returns initialized SDK client; may reuse cached instance.
  - `execute_chat(request: ChatRequest) -> ChatResponse` → handles non-streaming interactions with unified error translation.
  - `stream_chat(request: ChatRequest) -> Iterator[ChatChunk]` → yields streaming chunks and applies shared retry semantics.
- **`ChatOrchestrator`**
  - `prepare_request(params: OrchestrationParams) -> ChatRequest` → merges prompts, history, system instructions, and tool metadata.
  - `run_chat(request: OrchestrationParams, stream: bool)` → drives conversation, calling transport for responses and coordinating tool loops.
- **`ToolExecutionManager`**
  - `discover(tool_names: Iterable[str]) -> ToolCatalog`
  - `execute(call: ToolCallContext) -> ToolResult`
- **Factory / Composition Helpers**
  - A `create_llm_runtime(config: AssistantConfig)` helper wires together the adapter, transport, orchestrator, and tool manager.
  - Facades call the factory so consumers can continue instantiating `LLMClient()` or `AgentOrchestrator()` without awareness of internal components.

## Goals / Non-Goals
- Goals:
  - Provide a modular, multi-class design that isolates configuration, transport, orchestration, and tool execution responsibilities.
  - Preserve existing external capabilities (streaming, tool calls, history management) while reducing duplication.
  - Ensure the new structure adheres to PEP 8 conventions, includes type hints, and exposes clear extension points for additional providers or orchestrators.
- Non-Goals:
  - Introducing new LLM providers or transport protocols.
  - Redesigning the chat history or tool discovery subsystems beyond what is necessary for decoupling.

## Decisions
- Decision: Introduce a cohesive package (e.g., `assistant.llm.runtime`) that contains dedicated classes for `ConfigurationAdapter`, `TransportClient`, `ChatOrchestrator`, and `ToolExecutor`.
  - Rationale: Breaking the responsibilities into explicit collaborators reduces hidden coupling, makes dependencies injectable for tests, and clarifies public contracts.
- Decision: Provide a factory or top-level helper that maintains backward compatibility with existing import sites (`LLMClient`, `AgentOrchestrator`).
  - Rationale: Avoids a breaking change while consumers migrate to the new APIs incrementally.
- Decision: Centralize error handling and retry logic within the transport/orchestration boundary so both streaming and non-streaming flows share the same logic.
  - Rationale: Ensures consistent behavior and eliminates duplicated retry code paths.

## Risks / Trade-offs
- Risk: Hidden coupling in downstream consumers could rely on current private attributes.
  - Mitigation: Audit imports/usages before refactor; provide shim properties or deprecation warnings where necessary.
- Risk: Increased class count could add complexity if responsibilities are not clearly documented.
  - Mitigation: Supply inline documentation and high-level overview to guide contributors.
- Risk: Potential regressions in tool execution due to new abstractions.
  - Mitigation: Expand automated tests across streaming, tool invocation, and retry scenarios.

## Migration Plan
1. Implement new classes alongside existing ones.
2. Update internal references within `agent_client.py` and `client.py` to delegate to the new structure.
3. Ensure public entry points (`LLMClient`, `AgentOrchestrator`) expose the new functionality while maintaining existing method signatures until consumers are updated.
4. Remove legacy implementations once all call sites rely on the refactored classes.

## Open Questions
- Are there external integrations (e.g., MCP) that import these modules directly and require coordination?
- Should configuration defaults remain in `AssistantConfig`, or do we introduce provider-specific config objects now?
