"""
Tool Registry for FSC Assistant

This module manages all available tools that can be used by the assistant.
"""

from typing import Dict, List, Type, Optional
from .base_tool import BaseTool

# Import all tool modules to register them
from . import builtin, document, repository, tools, web, agent_discovery, change_directory


def _discover_tools() -> Dict[str, Type[BaseTool]]:
    """
    Discover and return all available tools by scanning imported modules.
    
    Returns:
        dict: Mapping of tool names to their classes
    """
    # Get all modules that have TOOL_REGISTRY
    import sys
    import inspect
    
    tool_registry = {}
    
    # Scan through the current module's globals for any registered tools
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, BaseTool) and obj != BaseTool:
            # This is a direct tool class - add it to registry
            tool_registry[obj.name] = obj
    
    # Also scan the imported modules for TOOL_REGISTRY lists
    for module_name in ['builtin', 'document', 'repository', 'tools', 'web', 'agent_discovery', 'change_directory']:
        try:
            module = getattr(sys.modules[__name__], module_name)
            if hasattr(module, 'TOOL_REGISTRY'):
                for tool_class in module.TOOL_REGISTRY:
                    if hasattr(tool_class, 'name') and tool_class.name:
                        tool_registry[tool_class.name] = tool_class
        except (AttributeError, ImportError):
            # Skip modules that don't have the expected structure
            continue
    
    return tool_registry


# Available tools registry - automatically populated by discovery
TOOL_REGISTRY: Dict[str, Type[BaseTool]] = _discover_tools()


def get_tool_by_name(name: str) -> Optional[Type[BaseTool]]:
    """
    Get a tool class by its name.
    
    Parameters:
        name (str): Name of the tool to retrieve
        
    Returns:
        Type[BaseTool]: The tool class if found, None otherwise
    """
    return TOOL_REGISTRY.get(name)


def get_all_tools() -> List[Type[BaseTool]]:
    """
    Get a list of all available tools.
    
    Returns:
        list: List of all available tool classes
    """
    return list(TOOL_REGISTRY.values())


def get_tool_names() -> List[str]:
    """
    Get a list of all available tool names.
    
    Returns:
        list: List of tool names
    """
    return list(TOOL_REGISTRY.keys())


# Export the main functions for easy access
__all__ = [
    'get_tool_by_name',
    'get_all_tools', 
    'get_tool_names',
    'TOOL_REGISTRY'
]