"""LLM integration and client management."""

from .agent_client import AgentOrchestrator
from .client import LLMClient
from .history import LLMChatHistoryManager

# Backward compatibility alias
LLMAgentClient = AgentOrchestrator

__all__ = [
    "LLMClient",
    "AgentOrchestrator",
    "LLMAgentClient",
    "LLMChatHistoryManager",
]
