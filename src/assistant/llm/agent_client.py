"""
Refactored Agent Client implementing Python best practices and OOP design principles.

This module provides a refactored implementation of the LLM agent client with:
- Proper separation of concerns
- Single responsibility principle
- Improved error handling
- Comprehensive type hints and documentation

The original implementation has been refactored into agent_client_refactored.py for better maintainability.
"""

# This file is deprecated. Please use agent_client_refactored.py instead.
# The refactored version implements all the same functionality with:
# - Proper separation of concerns 
# - Single responsibility principle
# - Improved error handling and logging
# - Comprehensive type hints and documentation
# - Better code organization following Python best practices

from .agent_client_refactored import AgentOrchestrator

# Re-export the refactored class for backward compatibility
__all__ = ["AgentOrchestrator"]