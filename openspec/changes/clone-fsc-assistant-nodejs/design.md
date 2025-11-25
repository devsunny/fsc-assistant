# Design: FSC Assistant Node.js Implementation

## Overview

This document outlines the architectural approach for implementing a Node.js version of FSC Assistant that maintains feature parity with the existing Python implementation while leveraging Node.js ecosystem advantages.

## Architecture Approach

### Core Components

1. **CLI Interface**: Match the Python CLI structure using Commander.js or similar
2. **Configuration Manager**: Handle TOML configuration parsing and management  
3. **LLM Orchestrator**: Integrate with OpenAI, Anthropic, and other LLM providers via Node.js SDKs
4. **Tool Repository**: Maintain list of available tools that can be invoked by the agent
5. **Shell Interface**: Interactive terminal experience with multi-line input support
6. **History Manager**: Track conversation history for context

### Technology Stack

- **Language**: TypeScript (for type safety)
- **Framework**: Node.js runtime 
- **CLI Library**: Commander.js or yargs
- **LLM Integration**: OpenAI SDK, Anthropic SDK, and generic HTTP clients
- **Configuration**: toml-node or similar TOML parser
- **Terminal UI**: Inquirer.js or similar for interactive prompts
- **File System**: Built-in Node.js fs module
- **HTTP Client**: Axios or node-fetch
- **Testing**: Jest or Mocha

### Module Structure

```
src/
├── cli.ts              # CLI entry point
├── config/             # Configuration management  
│   ├── manager.ts      # Config loading and parsing
│   └── types.ts        # Type definitions for configs
├── llm/                # LLM orchestration layer
│   ├── agent_client.ts # Agent orchestrator 
│   ├── models.ts       # Model selection and configuration
│   └── types.ts        # LLM related type definitions
├── agents/             # AI agents and shell interface
│   ├── shell.ts        # Interactive shell implementation
│   ├── tools/          # Tool repository
│   │   ├── file_system.ts
│   │   ├── system_shell.ts  
│   │   ├── web/
│   │   │   ├── webpage.ts
│   │   │   ├── screenshot.ts
│   │   │   └── google_search.ts
│   │   ├── integrations/
│   │   │   ├── jira.ts
│   │   │   └── github.ts
│   │   └── utils/      # Utility functions for tools
│   └── query_analyzer.ts # Intent analysis 
├── utils/              # General utilities
└── types.ts            # Shared type definitions
```

## Key Design Decisions

### 1. Lazy Loading Strategy

Similar to Python version, we'll implement lazy loading of heavy dependencies:
- LLM clients loaded only when needed
- Integration libraries (JIRA, GitHub) loaded on demand 
- Web scraping tools loaded only when used

### 2. Tool System Architecture

Tools will be implemented as functions that can be dynamically discovered and invoked:
- Tools registered in a central repository
- Each tool has clear input/output contracts  
- Tools are passed to LLM for function calling
- Support for both built-in and plugin-style tools

### 3. Configuration Management

Configuration will maintain the same TOML format but parsed using Node.js libraries:
- Same configuration file structure 
- Environment variable support
- Default values handling
- Validation mechanisms

### 4. Error Handling

Consistent error handling patterns:
- Graceful degradation when services are unavailable
- Clear error messages for missing configurations
- Retry logic for external API calls
- Logging system with appropriate verbosity levels

## Migration Considerations

### Tool Function Signatures

We'll maintain the same function signatures where possible to ensure compatibility:
- All tool functions will have consistent input/output patterns
- Parameter names and types will match Python versions when feasible
- Error handling will be adapted for Node.js conventions

### Performance Characteristics

Node.js implementation should maintain similar performance characteristics:
- Fast startup times (lazy loading)
- Efficient memory usage 
- Optimized I/O operations
- Minimal blocking operations

## Integration Points

### LLM Providers

We'll support the same providers as Python version:
- OpenAI API
- Anthropic Claude API  
- Other major LLM providers via generic HTTP interface

### External Services

Integration with external services will be implemented using official Node.js SDKs where available:
- GitHub: @octokit/rest 
- JIRA: jira-client or similar
- Web APIs: Direct HTTP calls with appropriate libraries

## Testing Strategy

1. Unit tests for individual components and tools
2. Integration tests for LLM interactions  
3. End-to-end shell testing
4. Cross-platform compatibility verification
5. Performance benchmarking against Python version

## Deployment Considerations

### Package Structure

The npm package will be structured to match the Python package:
- Main entry point: `fsc`
- Same command-line interface 
- Configuration file handling (`.fsc-assistant.env.toml`)

### Dependencies

We'll maintain a similar dependency set but adapted for Node.js ecosystem:
- Core LLM libraries
- HTTP clients and utilities  
- CLI frameworks
- File system operations
- Testing tools