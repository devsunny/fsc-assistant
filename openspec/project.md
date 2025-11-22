# Project Context

## Purpose
The FSC Assistant is a command-line tool designed to leverage Large Language Model's coding capability to help build software with ease. It serves as an AI-powered development assistant that helps with code generation, review, refactoring, testing, and more using large language models (LLMs) and Model Context Protocol (MCP).

## Tech Stack
- Python 3.12+ (with support for 3.13 and 3.14)
- Click - Command-line interface framework
- OpenAI API client - LLM integration
- Docling - Document processing library
- Rich - Terminal formatting and display
- Prompt Toolkit - Interactive command line interfaces
- Tenacity - Retry logic
- PyGithub - GitHub integration
- Jira - Jira integration
- FastMCP - Model Context Protocol implementation
- Setuptools - Python packaging

## Project Conventions

### Code Style
- Python 3.12+ with type hints
- PEP 8 style guide compliance
- Docstring documentation using Google-style docstrings
- Modular structure following the `src/` directory pattern
- Class and function names use snake_case
- Constants are uppercase with underscores
- All modules should be importable from the main package namespace

### Architecture Patterns
- Lazy loading of heavy dependencies for fast CLI startup
- Command-based architecture using Click framework
- Plugin-style agent system for integrations (GitHub, Jira)
- Configuration management through a centralized config manager
- Separation of concerns between LLM interactions and tooling
- Dependency injection pattern where appropriate

### Testing Strategy
- Unit tests in the `tests/` directory
- Integration tests for external services (LLM, GitHub, Jira)
- Test coverage focused on core functionality and edge cases
- Mock external dependencies during testing
- CI pipeline with automated test execution

### Git Workflow
- Feature branching strategy
- Semantic versioning following MAJOR.MINOR.PATCH format
- Commit messages using conventional commit style
- Pull requests for all changes
- Main branch protected, requiring review before merge

## Domain Context
This project is an AI-powered development assistant that integrates with LLMs to help developers write code. It supports:
- Code generation and completion
- Document processing (using Docling)
- Integration with GitHub repositories
- Jira issue management
- Interactive shell for development tasks
- Configuration management for various services

## Important Constraints
- Must support Python 3.12+ environments
- All external API integrations must handle rate limiting gracefully
- LLM configuration is required before most operations can proceed
- Security considerations around API keys and credentials in configuration files
- Performance constraints due to heavy dependencies that are lazily loaded

## External Dependencies
- OpenAI API - Primary LLM integration
- GitHub API - Repository and issue management
- Jira API - Issue tracking system integration
- Model Context Protocol (MCP) - Communication protocol for AI agents
- Docling - Document processing library for PDFs and documents