## Why
The current LLM client layer is split across `src/assistant/llm/client.py` and `src/assistant/llm/agent_client.py`, leading to duplicate configuration logic, overlapping responsibilities, and brittle state management. This fragmentation makes it difficult to reason about how requests flow from configuration to the orchestrator, increases the risk of divergence between streaming and non-streaming pathways, and prevents the module from following consistent PEP 8 and OO design practices.

## What Changes
- Introduce a unified, modular multi-class implementation that consolidates `LLMClient` and `AgentOrchestrator` responsibilities behind a cohesive package structure.
- Formalize separation of concerns between configuration, transport/client setup, request orchestration, and tool execution so each class has a single, testable role.
- Standardize naming, logging, and error-handling patterns to align with PEP 8 best practices and maintainable OOP design.
- Provide explicit extension points for future providers and orchestration strategies without duplicating configuration code.

## Impact
- Affected specs: New `llm-clients` capability describing the unified client/orchestrator responsibilities.
- Affected code: `src/assistant/llm/client.py`, `src/assistant/llm/agent_client.py`, related helper modules under `src/assistant/llm/` and any import sites that consume these classes.
- Tooling/tests: Requires updates to unit/integration tests that instantiate either client, and regression coverage for streaming + tool-invocation flows.
