"""Factory helpers wiring up the unified LLM runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from assistant.llm.history import LLMChatHistoryManager

from .config import LLMConfigurationAdapter, LLMProviderConfig
from .orchestrator import ChatOrchestrator
from .tools import ToolExecutionManager
from .transport import LLMTransportClient


@dataclass
class LLMRuntime:
    """Container holding the composed runtime collaborators."""

    config_adapter: LLMConfigurationAdapter
    provider_config: LLMProviderConfig
    transport: LLMTransportClient
    tool_manager: ToolExecutionManager
    orchestrator: ChatOrchestrator
    history_manager: LLMChatHistoryManager


def create_llm_runtime(
    *, config_adapter: Optional[LLMConfigurationAdapter] = None, history_path: Optional[str] = None
) -> LLMRuntime:
    """Create and compose the runtime objects used by the LLM facades."""
    adapter = config_adapter or LLMConfigurationAdapter()
    provider_config = adapter.load_provider_config()
    history_manager = LLMChatHistoryManager(history_file_path=history_path)
    transport = LLMTransportClient(provider_config)
    tool_manager = ToolExecutionManager()
    orchestrator = ChatOrchestrator(
        provider_config=provider_config,
        transport=transport,
        tool_manager=tool_manager,
        history_manager=history_manager,
    )
    return LLMRuntime(
        config_adapter=adapter,
        provider_config=provider_config,
        transport=transport,
        tool_manager=tool_manager,
        orchestrator=orchestrator,
        history_manager=history_manager,
    )
