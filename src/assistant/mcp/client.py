"""
FastMCP Client Wrapper for fsc-assistant.

This module provides a synchronous wrapper around the fastmcp library's Client class,
supporting stdio, SSE, and HTTP transports for connecting to MCP servers.

The wrapper handles async-to-sync conversion and provides integration-specific methods
for OpenAI tool format conversion and string-based tool execution.

Example Usage:
    Basic connection and tool listing:

    >>> config = {
    ...     "transport": "http",
    ...     "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=..."
    ... }
    >>> client = FastMCPClient("tavily", config)
    >>> client.connect()
    True
    >>> tools = client.list_tools()
    >>> client.disconnect()

    Using context manager:

    >>> with FastMCPClient("tavily", config) as client:
    ...     tools = client.get_tools_openai_format()
    ...     result = client.execute("search", {"query": "Python"})

    Configuration formats:

    HTTP/SSE transport:
    {
        "transport": "http",
        "url": "https://server.com/mcp",
        "headers": {"Authorization": "Bearer ${API_KEY}"}
    }

    Stdio transport:
    {
        "transport": "stdio",
        "command": "node",
        "args": ["server.js"],
        "env": {"API_KEY": "${MY_API_KEY}"}
    }
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from fastmcp import Client as _FastMCPAsyncClient
from mcp import types as mcp_types

logger = logging.getLogger(__name__)


class FastMCPClient:
    """
    Synchronous wrapper for fastmcp.Client.

    Provides a synchronous interface to the async fastmcp.Client, supporting
    multiple transport types (stdio, SSE, HTTP) and integration-specific methods
    for OpenAI tool format conversion and string-based execution.

    This wrapper maintains backward compatibility with the previous custom
    implementation while leveraging the fastmcp library for protocol handling.

    Attributes:
        server_name: Name of the MCP server
        config: Server configuration dictionary
        transport_type: Type of transport (stdio, sse, http)
        connected: Whether the client is connected
    """

    def __init__(self, server_name: str, config: Dict[str, Any]):
        """
        Initialize FastMCP client wrapper.

        Args:
            server_name: Name of the MCP server
            config: Server configuration with transport details
                Expected format:
                {
                    "transport": "http",  # or "stdio", "sse"
                    "url": "https://...",  # for http/sse
                    "command": "node server.js",  # for stdio
                    "args": [],  # optional, for stdio
                    "env": {},  # optional environment variables
                    "headers": {},  # optional HTTP headers
                    "require_approval": "never",  # optional
                    "auth": null  # optional
                }

        Raises:
            ValueError: If configuration is invalid
        """
        self.server_name = server_name
        self.config = config
        self.transport_type = config.get("transport", "stdio")
        self.connected = False
        self._client: Optional[_FastMCPAsyncClient] = None
        self._tools: List[Dict[str, Any]] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate server configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.transport_type not in ["stdio", "sse", "http"]:
            raise ValueError(
                f"Invalid transport type: {self.transport_type}. "
                "Must be one of: stdio, sse, http"
            )

        if self.transport_type == "stdio":
            if "command" not in self.config:
                raise ValueError("stdio transport requires 'command' in config")
        elif self.transport_type in ["sse", "http"]:
            if "url" not in self.config:
                raise ValueError(
                    f"{self.transport_type} transport requires 'url' in config"
                )

    def _substitute_env_vars(self, value: str) -> str:
        """
        Substitute environment variables in configuration values.

        Supports ${VAR_NAME} syntax for environment variable substitution.
        If the environment variable is not set, the literal string is kept.

        Args:
            value: String that may contain ${VAR_NAME} patterns

        Returns:
            String with environment variables substituted

        Example:
            >>> os.environ['API_KEY'] = 'secret123'
            >>> client._substitute_env_vars('Bearer ${API_KEY}')
            'Bearer secret123'
        """
        if not isinstance(value, str):
            return value

        # Simple ${VAR} substitution
        pattern = r"\$\{([^}]+)\}"

        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(pattern, replacer, value)

    def _prepare_transport_config(self) -> Dict[str, Any]:
        """
        Prepare transport configuration for fastmcp.Client.

        Maps the config dict format to fastmcp.Client parameters.

        Returns:
            Dictionary suitable for fastmcp.Client initialization
        """
        transport_config = {}

        if self.transport_type == "stdio":
            # For stdio, we need to provide command and args
            command = self.config["command"]
            args = self.config.get("args", [])

            # Prepare environment variables
            env = os.environ.copy()
            if "env" in self.config:
                for key, value in self.config["env"].items():
                    env[key] = self._substitute_env_vars(value)

            # fastmcp expects a dict with command, args, and env
            transport_config = {"command": command, "args": args, "env": env}

        elif self.transport_type in ["sse", "http"]:
            # For HTTP/SSE, provide the URL
            url = self._substitute_env_vars(self.config["url"])
            transport_config = url

            # Add headers if provided
            if "headers" in self.config:
                headers = {}
                for key, value in self.config["headers"].items():
                    headers[key] = self._substitute_env_vars(value)
                # Note: fastmcp may handle headers differently
                # This might need adjustment based on actual fastmcp API

        return transport_config

    def _run_async(self, coro):
        """
        Run an async coroutine synchronously.

        Creates or reuses an event loop to execute the coroutine.

        Args:
            coro: Coroutine to run

        Returns:
            Result of the coroutine
        """
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def connect(self) -> bool:
        """
        Connect to the MCP server.

        Establishes connection using the configured transport and fetches
        the list of available tools.

        Returns:
            True if connection successful, False otherwise

        Example:
            >>> client = FastMCPClient("tavily", config)
            >>> if client.connect():
            ...     print(f"Connected with {len(client.list_tools())} tools")
        """
        try:
            # Prepare transport configuration
            transport_config = self._prepare_transport_config()

            # Create fastmcp.Client instance
            self._client = _FastMCPAsyncClient(transport_config)

            # Connect using async context manager
            async def _connect():
                await self._client.__aenter__()
                # Fetch available tools
                tools = await self._client.list_tools()
                return tools

            tools = self._run_async(_connect())

            # Convert MCP Tool objects to dicts
            self._tools = [self._tool_to_dict(tool) for tool in tools]

            self.connected = True
            logger.info(
                f"Connected to {self.server_name} via {self.transport_type} "
                f"with {len(self._tools)} tools"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.server_name}: {e}")
            if self._client:
                try:
                    self._run_async(self._client.__aexit__(None, None, None))
                except:
                    pass
                self._client = None
            return False

    def _tool_to_dict(self, tool: mcp_types.Tool) -> Dict[str, Any]:
        """
        Convert MCP Tool object to dictionary.

        Args:
            tool: MCP Tool object from fastmcp

        Returns:
            Dictionary representation of the tool with name, description, and inputSchema
        """
        return {
            "name": tool.name,
            "description": tool.description or "",
            "inputSchema": tool.inputSchema if hasattr(tool, "inputSchema") else {},
        }

    def disconnect(self) -> None:
        """
        Disconnect from the MCP server and cleanup resources.

        Always marks the client as disconnected, even if cleanup fails.
        Logs errors but does not raise exceptions.

        Example:
            >>> client.connect()
            >>> # ... use client ...
            >>> client.disconnect()
        """
        try:
            if self._client:

                async def _disconnect():
                    await self._client.__aexit__(None, None, None)

                self._run_async(_disconnect())
                self._client = None

            logger.info(f"Disconnected from {self.server_name}")

        except Exception as e:
            logger.error(f"Error disconnecting from {self.server_name}: {e}")
        finally:
            # Always mark as disconnected, even if cleanup fails
            self.connected = False

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.

        Fetches the current list of tools from the server and caches them.

        Returns:
            List of tool definitions in MCP format, each containing:
            - name: Tool name
            - description: Tool description
            - inputSchema: JSON Schema for tool parameters

        Example:
            >>> tools = client.list_tools()
            >>> for tool in tools:
            ...     print(f"{tool['name']}: {tool['description']}")
        """
        if not self.connected or not self._client:
            logger.warning(f"Not connected to {self.server_name}")
            return []

        try:

            async def _list_tools():
                tools = await self._client.list_tools()
                return tools

            tools = self._run_async(_list_tools())
            self._tools = [self._tool_to_dict(tool) for tool in tools]
            return self._tools

        except Exception as e:
            logger.error(f"Failed to list tools from {self.server_name}: {e}")
            return []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.

        Executes the specified tool with the given arguments and returns
        the raw result from the server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary

        Returns:
            Tool execution result (typically a list of content items)

        Raises:
            RuntimeError: If not connected or tool call fails

        Example:
            >>> result = client.call_tool("search", {"query": "Python"})
            >>> print(result)
        """
        if not self.connected or not self._client:
            raise RuntimeError(f"Not connected to {self.server_name}")

        try:
            logger.info(f"Calling tool {tool_name} on {self.server_name}")
            logger.debug(f"Arguments: {arguments}")

            async def _call_tool():
                result = await self._client.call_tool(tool_name, arguments or {})
                return result

            result = self._run_async(_call_tool())

            logger.info(f"Tool {tool_name} completed successfully")

            # Extract content from CallToolResult
            if hasattr(result, "content"):
                # Return the content list
                return [self._content_to_dict(c) for c in result.content]

            return result

        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise RuntimeError(f"Tool call failed: {e}")

    def _content_to_dict(self, content) -> Dict[str, Any]:
        """
        Convert MCP Content object to dictionary.

        Args:
            content: MCP Content object

        Returns:
            Dictionary representation
        """
        if hasattr(content, "model_dump"):
            return content.model_dump()
        elif hasattr(content, "dict"):
            return content.dict()
        else:
            return {"type": "text", "text": str(content)}

    def to_openai_tool_format(self, mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP tool schema to OpenAI function calling format.

        Prefixes tool name with server name to avoid conflicts and stores
        metadata for routing tool calls back to the correct server.

        Args:
            mcp_tool: MCP tool definition dictionary

        Returns:
            Tool in OpenAI function calling format with structure:
            {
                "type": "function",
                "function": {
                    "name": "<server>_<tool>",
                    "description": "...",
                    "parameters": {...}
                },
                "_mcp_server": "<server>",
                "_mcp_tool_name": "<tool>"
            }

        Example:
            >>> tool = {"name": "search", "description": "Search the web", "inputSchema": {...}}
            >>> openai_tool = client.to_openai_tool_format(tool)
            >>> print(openai_tool["function"]["name"])
            'tavily_search'
        """
        # Prefix tool name with server name to avoid conflicts
        tool_name = f"{self.server_name}_{mcp_tool['name']}"

        openai_tool = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": mcp_tool.get("description", ""),
                "parameters": mcp_tool.get(
                    "inputSchema", {"type": "object", "properties": {}, "required": []}
                ),
            },
        }

        # Add metadata to track source
        openai_tool["_mcp_server"] = self.server_name
        openai_tool["_mcp_tool_name"] = mcp_tool["name"]

        return openai_tool

    def convert_tool_to_openai_format(self, mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP tool schema to OpenAI function calling format.

        Alias for to_openai_tool_format() for backward compatibility.

        Args:
            mcp_tool: MCP tool definition

        Returns:
            Tool in OpenAI function calling format
        """
        return self.to_openai_tool_format(mcp_tool)

    def get_tools_openai_format(self) -> List[Dict[str, Any]]:
        """
        Get all tools in OpenAI function calling format.

        Fetches all tools from the server and converts them to OpenAI format.

        Returns:
            List of tools in OpenAI function calling format

        Example:
            >>> openai_tools = client.get_tools_openai_format()
            >>> # Pass to OpenAI API
            >>> response = openai.chat.completions.create(
            ...     model="gpt-4",
            ...     messages=[...],
            ...     tools=openai_tools
            ... )
        """
        tools = self.list_tools()
        return [self.to_openai_tool_format(tool) for tool in tools]

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool and return the result as a string.

        This method is designed for LLM integration where string output
        is required. Complex results are converted to JSON strings, and
        MCP content items are extracted and joined.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary

        Returns:
            String representation of the tool result

        Raises:
            RuntimeError: If not connected or tool call fails

        Example:
            >>> result_str = client.execute("search", {"query": "Python"})
            >>> print(result_str)
            'Python is a high-level programming language...'
        """
        try:
            result = self.call_tool(tool_name, arguments)

            # Convert result to string
            if isinstance(result, str):
                return result
            elif isinstance(result, list):
                # Handle list of content items (typical MCP response)
                text_parts = []
                for item in result:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        else:
                            text_parts.append(json.dumps(item, indent=2))
                    else:
                        text_parts.append(str(item))
                return "\n".join(text_parts)
            elif isinstance(result, dict):
                return json.dumps(result, indent=2)
            else:
                return str(result)

        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise RuntimeError(f"Tool execution failed: {e}")

    def __enter__(self):
        """
        Context manager entry.

        Automatically connects to the server.

        Example:
            >>> with FastMCPClient("tavily", config) as client:
            ...     tools = client.list_tools()
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.

        Automatically disconnects from the server.
        """
        self.disconnect()
        return False

    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self.connected else "disconnected"
        return f"FastMCPClient(server={self.server_name}, transport={self.transport_type}, status={status})"
