## 1. Research & Planning
- [x] 1.1 Catalogue current responsibilities of `LLMClient` and `AgentOrchestrator`, including configuration, history, and tool workflows.
- [x] 1.2 Confirm existing consumers (CLI commands, agents, tests) that import these classes to avoid regressions.

## 2. Architecture
- [x] 2.1 Draft target class diagram showing configuration, transport, orchestration, and tool-handling layers.
- [x] 2.2 Define public interfaces and dependency boundaries (factories, injectable collaborators).

## 3. Implementation
- [x] 3.1 Create new package/module structure that exposes the refactored multi-class design while maintaining backwards-compatible entry points as needed.
- [x] 3.2 Migrate configuration and transport logic into dedicated components and update imports.
- [x] 3.3 Refactor orchestration logic to delegate to the new components, ensuring streaming and non-streaming paths share common code.
- [x] 3.4 Update tool execution handling to use the new abstractions and remove duplicated state.
- [x] 3.5 Remove or deprecate obsolete code paths in `client.py` and `agent_client.py` in favor of the new implementation.

## 4. Quality
- [x] 4.1 Update or add unit/integration tests for streaming, non-streaming, and tool-invocation scenarios.
- [x] 4.2 Run `openspec validate refactor-llm-client-module --strict` and ensure it passes.
- [x] 4.3 Execute relevant test suites (e.g., `pytest tests/assistant/llm` or equivalent) and document results.
