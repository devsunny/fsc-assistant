## MODIFIED Requirements

### Requirement: Shell Startup Performance
The shell command SHALL initialize and display the welcome message within 500 milliseconds on standard development hardware.

#### Scenario: Cold start performance
- **GIVEN** a fresh shell invocation
- **WHEN** the user runs `fsc-assistant shell`
- **THEN** the welcome message appears within 500ms
- **AND** the shell is ready to accept input

#### Scenario: Lazy loading of heavy dependencies
- **GIVEN** the shell has started
- **WHEN** the user has not yet executed any LLM queries
- **THEN** heavy dependencies (openai, tenacity, transformers) SHALL NOT be loaded
- **AND** the shell SHALL remain responsive to basic commands

#### Scenario: On-demand LLM initialization
- **GIVEN** the shell is running with lazy-loaded components
- **WHEN** the user submits their first LLM query
- **THEN** the AgentOrchestrator SHALL initialize transparently
- **AND** the query SHALL be processed normally
- **AND** subsequent queries SHALL use the initialized orchestrator