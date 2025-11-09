"""
In-memory tools repository for centralized tool management.

This module provides a centralized registry for all tools (builtin, integrations, MCP)
with category-based organization and thread-safe operations.
"""

import logging
import threading
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class InMemoryToolsRepository:
    """
    Centralized repository for managing all available tools.
    
    Provides thread-safe registration and retrieval of tools organized by category.
    Supports builtin tools, integration tools (JIRA, GitHub, LiteLLM), and MCP tools.
    
    Attributes:
        _tools: Dictionary mapping tool names to tool functions
        _tool_categories: Dictionary mapping tool names to categories
        _lock: Thread lock for thread-safe operations
    """
    
    def __init__(self):
        """Initialize an empty tools repository."""
        self._tools: Dict[str, Callable] = {}
        self._tool_categories: Dict[str, str] = {}
        self._lock = threading.Lock()
        logger.debug("Initialized InMemoryToolsRepository")
    
    def register_tool(self, tool: Callable, category: str = "builtin") -> None:
        """
        Register a single tool with the repository.
        
        Args:
            tool: Tool function to register
            category: Category for the tool (e.g., "builtin", "integration", "mcp")
        """
        with self._lock:
            tool_name = tool.__name__
            
            # Warn if overwriting existing tool
            if tool_name in self._tools:
                logger.warning(f"Overwriting existing tool: {tool_name}")
            
            self._tools[tool_name] = tool
            self._tool_categories[tool_name] = category
            logger.debug(f"Registered tool '{tool_name}' in category '{category}'")
    
    def register_tools(self, tools: List[Callable], category: str) -> None:
        """
        Register multiple tools with the repository.
        
        Args:
            tools: List of tool functions to register
            category: Category for all tools
        """
        for tool in tools:
            self.register_tool(tool, category)
        logger.info(f"Registered {len(tools)} tools in category '{category}'")
    
    def get_all_tools(self) -> List[Callable]:
        """
        Get all registered tools.
        
        Returns:
            List of all tool functions
        """
        with self._lock:
            tools = list(self._tools.values())
            logger.debug(f"Retrieved {len(tools)} tools")
            return tools
    
    def get_tools_by_category(self, category: str) -> List[Callable]:
        """
        Get tools by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tool functions in the specified category
        """
        with self._lock:
            tools = [
                self._tools[name]
                for name, cat in self._tool_categories.items()
                if cat == category
            ]
            logger.debug(f"Retrieved {len(tools)} tools from category '{category}'")
            return tools
    
    def get_tool_metadata(self, format: str = "simple") -> List[Dict[str, Any]]:
        """
        Get metadata for all registered tools.
        
        Args:
            format: Format for metadata ("simple" or "openai")
            
        Returns:
            List of tool metadata dictionaries
        """
        with self._lock:
            metadata = []
            for name, tool in self._tools.items():
                category = self._tool_categories.get(name, "unknown")
                
                if format == "openai":
                    # OpenAI function calling format
                    tool_meta = {
                        "type": "function",
                        "function": {
                            "name": name,
                            "description": tool.__doc__ or f"Tool: {name}",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        "_category": category
                    }
                else:
                    # Simple format
                    tool_meta = {
                        "name": name,
                        "description": tool.__doc__ or f"Tool: {name}",
                        "category": category
                    }
                
                metadata.append(tool_meta)
            
            logger.debug(f"Retrieved metadata for {len(metadata)} tools (format={format})")
            return metadata
    
    def get_tool_count(self) -> int:
        """
        Get total number of registered tools.
        
        Returns:
            Number of tools
        """
        with self._lock:
            return len(self._tools)
    
    def get_category_counts(self) -> Dict[str, int]:
        """
        Get count of tools per category.
        
        Returns:
            Dictionary mapping category names to tool counts
        """
        with self._lock:
            counts: Dict[str, int] = {}
            for category in self._tool_categories.values():
                counts[category] = counts.get(category, 0) + 1
            logger.debug(f"Category counts: {counts}")
            return counts
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Tool name to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        with self._lock:
            return name in self._tools
    
    def __repr__(self) -> str:
        """String representation of the repository."""
        return f"InMemoryToolsRepository(tools={self.get_tool_count()}, categories={len(set(self._tool_categories.values()))})"
