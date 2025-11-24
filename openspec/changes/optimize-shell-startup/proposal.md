## Why
The "fsc shell" command has a slow startup time of approximately 2.8 seconds, with profiling showing that 2.5 seconds (89%) is spent importing the `agent_client` module and its heavy dependencies (openai, tenacity, etc.). This poor user experience makes the shell feel unresponsive and discourages frequent use.

## What Changes
- Implement lazy loading for heavy LLM client dependencies in `agent_client.py`
- Optimize import structure in `shell.py` to defer non-critical imports until needed
- Move tool loading to be on-demand rather than during shell initialization
- Add lazy initialization pattern for `AgentOrchestrator` to defer heavy object creation
- Maintain all existing functionality while improving startup performance by 60-80%

## Impact
- **Affected specs**: `specs/shell/spec.md` - Shell startup performance requirements
- **Affected code**: 
  - `src/assistant/agents/shell.py` - Main shell implementation
  - `src/assistant/llm/agent_client.py` - LLM client with heavy dependencies
  - `src/assistant/agents/agent_repo.py` - Tool loading logic
- **Performance target**: Reduce startup time from ~2.8s to <0.5s
- **No breaking changes**: All existing commands and functionality preserved