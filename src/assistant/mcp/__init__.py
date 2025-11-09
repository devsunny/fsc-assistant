"""
MCP (Model Context Protocol) integration for fsc-assistant.

This module provides FastMCP 2.0 client wrapper for connecting to external
MCP servers and using their tools in the AgenticShell.
"""


# Lazy imports to avoid circular dependencies and import issues
def __getattr__(name):
    if name == "FastMCPClient":
        from assistant.mcp.client import FastMCPClient

        return FastMCPClient
    elif name == "MCPRegistry":
        from assistant.mcp.registry import MCPRegistry

        return MCPRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["FastMCPClient", "MCPRegistry"]
