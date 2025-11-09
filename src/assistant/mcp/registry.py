"""
MCP Server Registry Management.

This module provides registry management for MCP servers, including
loading from configuration files, enabling/disabling servers, and
managing server lifecycle.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from assistant.mcp.client import FastMCPClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MCPRegistry:
    """
    MCP Server Registry Manager.

    Manages MCP server configurations, connections, and lifecycle.
    Supports loading from JSON configuration files and runtime
    enable/disable of servers.

    Attributes:
        registry_path: Path to the registry JSON file
        servers: Dictionary of server configurations
        clients: Dictionary of active FastMCPClient instances
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize MCP Registry.

        Args:
            registry_path: Path to registry JSON file. If None, uses default.
        """
        self.registry_path = self._resolve_registry_path(registry_path)
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, FastMCPClient] = {}

        # Load registry if file exists
        if self.registry_path and self.registry_path.exists():
            logger.info("loading from file: %s", self.registry_path)
            print(f"loading from file:{ self.registry_path}")
            self.load_from_file()

    def _resolve_registry_path(self, registry_path: Optional[str]) -> Optional[Path]:
        """
        Resolve registry file path.

        Args:
            registry_path: User-provided path or None

        Returns:
            Resolved Path object or None
        """
        if registry_path:
            path = Path(registry_path).expanduser()
            return path

        # Default path
        default_path = Path.home() / ".fsc-assistant" / "mcp.json"
        return default_path if default_path.exists() else None

    def load_from_file(self, file_path: Optional[str] = None) -> None:
        """
        Load server configurations from JSON file.

        Args:
            file_path: Path to JSON file. If None, uses registry_path.

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(file_path).expanduser() if file_path else self.registry_path

        if not path or not path.exists():
            logger.warning(f"Registry file not found: {path}")
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)

            # Support both flat and nested formats
            if "mcpServers" in data:
                self.servers = data["mcpServers"]
            else:
                self.servers = data

            logger.info(f"Loaded {len(self.servers)} servers from {path}")
            # Validate server configurations
            self._validate_servers()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in registry file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            raise

    def _validate_servers(self) -> None:
        """Validate all server configurations."""
        for server_name, config in self.servers.items():
            try:
                self._validate_server_config(server_name, config)
            except ValueError as e:
                logger.exception(e)
                logger.warning(f"Invalid config for {server_name}: {e}")

    def _validate_server_config(self, server_name: str, config: Dict[str, Any]) -> None:
        """
        Validate a single server configuration.

        Args:
            server_name: Name of the server
            config: Server configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        if "transport" not in config:
            raise ValueError(f"Server {server_name} missing 'transport' field")

        transport = config["transport"]
        if transport not in ["stdio", "sse", "http"]:
            raise ValueError(f"Invalid transport type: {transport}")

        if transport == "stdio" and "command" not in config:
            raise ValueError(f"stdio transport requires 'command' field")

        if transport in ["sse", "http"] and "url" not in config:
            raise ValueError(f"{transport} transport requires 'url' field")

    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all enabled server configurations.

        Returns:
            Dictionary of enabled server configurations
        """
        return {
            name: config
            for name, config in self.servers.items()
            if config.get("enabled", False)
        }

    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific server.

        Args:
            server_name: Name of the server

        Returns:
            Server configuration or None if not found
        """
        return self.servers.get(server_name)

    def list_servers(self) -> List[str]:
        """
        List all configured server names.

        Returns:
            List of server names
        """
        return list(self.servers.keys())

    def enable_servers(self) -> bool:
        for server_name in self.servers:
            self.enable_server(server_name)

    def enable_server(self, server_name: str) -> bool:
        """
        Enable a server at runtime.

        Args:
            server_name: Name of the server to enable

        Returns:
            True if successful, False otherwise
        """
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found in registry")
            return False

        try:
            # Mark as enabled
            logger.info(f"Enabling server {server_name}")
            self.servers[server_name]["enabled"] = True

            # Connect if not already connected
            if server_name not in self.clients:
                client = FastMCPClient(server_name, self.servers[server_name])
                if client.connect():
                    self.clients[server_name] = client
                    logger.info(f"Enabled and connected to {server_name}")
                    return True
                else:
                    logger.error(f"Failed to connect to {server_name}")
                    return False

            logger.info(f"Server {server_name} already connected")
            return True

        except Exception as e:
            logger.error(f"Failed to enable {server_name}: {e}")
            return False

    def disable_server(self, server_name: str) -> bool:
        """
        Disable a server at runtime.

        Args:
            server_name: Name of the server to disable

        Returns:
            True if successful, False otherwise
        """
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found in registry")
            return False

        try:
            # Mark as disabled
            self.servers[server_name]["enabled"] = False

            # Disconnect if connected
            if server_name in self.clients:
                self.clients[server_name].disconnect()
                del self.clients[server_name]
                logger.info(f"Disabled and disconnected from {server_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to disable {server_name}: {e}")
            return False

    def connect_enabled_servers(self) -> Dict[str, bool]:
        """
        Connect to all enabled servers.

        Returns:
            Dictionary mapping server names to connection success status
        """
        results = {}
        enabled_servers = self.get_enabled_servers()

        for server_name, config in enabled_servers.items():
            try:
                if server_name not in self.clients:
                    client = FastMCPClient(server_name, config)
                    success = client.connect()
                    if success:
                        self.clients[server_name] = client
                    results[server_name] = success
                else:
                    results[server_name] = True  # Already connected

            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
                results[server_name] = False

        return results

    def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        for server_name, client in list(self.clients.items()):
            try:
                client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")

        self.clients.clear()
        logger.info("Disconnected from all servers")

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools from all connected servers.

        Returns:
            List of tools in OpenAI function calling format
        """
        all_tools = []

        for server_name, client in self.clients.items():

            try:
                tools = client.get_tools_openai_format()
                all_tools.extend(tools)
            except Exception as e:
                logger.error(f"Failed to get tools from {server_name}: {e}")

        return all_tools

    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all servers.

        Returns:
            Dictionary with server status information
        """
        status = {}

        for server_name, config in self.servers.items():
            status[server_name] = {
                "enabled": config.get("enabled", False),
                "connected": server_name in self.clients,
                "transport": config.get("transport", "unknown"),
                "description": config.get("description", ""),
            }

        return status

    def __enter__(self):
        """Context manager entry."""
        self.connect_enabled_servers()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect_all()
        return False

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MCPRegistry(servers={len(self.servers)}, connected={len(self.clients)})"
        )
