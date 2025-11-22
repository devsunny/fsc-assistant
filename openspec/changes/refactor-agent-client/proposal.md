# Refactor Agent Client for Python Best Practices and OOP Design

## Summary

This change proposes a comprehensive refactoring of `fsc-assistant/src/assistant/llm/agent_client.py` to improve code quality, maintainability, and adherence to Python best practices and object-oriented design principles.

## Problem Statement

The current implementation has several issues that violate Python best practices and OOP principles:

1. **Code Complexity**: The file contains overly complex methods with multiple responsibilities
2. **Poor Separation of Concerns**: Mixes LLM interaction logic, tool execution, message handling, and error management 
3. **Inconsistent Naming**: Some variables use inconsistent naming conventions
4. **Magic Numbers/Strings**: Uses hardcoded values like `MAX_INPUT_TOKENS = 64000` without clear justification
5. **Code Duplication**: Similar logic exists in multiple methods (e.g., parameter handling)
6. **Lack of Type Safety**: Inconsistent type hints and missing documentation
7. **Global State Issues**: Direct access to global logger configuration

## Solution Overview

Refactor the `AgentOrchestrator` class to:
- Apply proper OOP principles with clear single responsibilities
- Implement design patterns where appropriate (Strategy, Factory)
- Improve code readability and maintainability 
- Add comprehensive type hints and documentation
- Separate concerns into logical components
- Use Python idioms and best practices

## Change Details

This is a substantial refactoring that will restructure the class while maintaining all existing functionality. The changes include:
- Breaking down large methods into smaller, focused functions
- Applying proper inheritance and composition patterns  
- Improving error handling and logging
- Adding comprehensive docstrings and type hints
- Implementing configuration management properly