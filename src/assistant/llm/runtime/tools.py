"""Tool discovery and execution helpers for the LLM runtime."""
from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from assistant.utils.json import CustomJsonEncoder

logger = logging.getLogger(__name__)


ToolCallable = Callable[..., Any]
ToolMeta = Dict[str, Any]
ToolMapping = Dict[str, Tuple[ToolCallable, bool]]
ToolMessages = List[Dict[str, Any]]


class ToolExecutionManager:
    """Co-ordinates tool discovery, deduplication, and execution."""

    def __init__(self, stream_handler: Optional[Callable[[str], None]] = None):
        self.stream_handler = stream_handler
        self._last_signature: Optional[Tuple[str, str, str]] = None

    def with_stream_handler(self, stream_handler: Optional[Callable[[str], None]] = None) -> "ToolExecutionManager":
        """Return a new manager that uses the provided stream handler."""
        clone = ToolExecutionManager(stream_handler=stream_handler)
        clone._last_signature = self._last_signature
        return clone

    def discover(self, tools: Optional[Iterable[Callable[..., Any]]]) -> Tuple[List[ToolMeta], ToolMapping]:
        """Resolve tool metadata and mapping using existing discovery helpers."""
        if not tools:
            return [], {}
        from assistant.agents.agent_discovery import discover_tools

        return discover_tools(tools)

    def execute(
        self,
        *,
        tool: ToolCallable,
        assistant_content: str,
        tool_call_id: str,
        tool_type: str,
        tool_name: str,
        tool_json_args: str,
        context: Optional[dict] = None,
    ) -> ToolMessages:
        """Execute a tool safely, returning call + result messages."""
        logger.info("tool execution %s - %s", tool_call_id, tool_name)

        signature = (tool_name, tool_json_args, assistant_content)
        messages: ToolMessages = [
            {
                "id": tool_call_id,
                "type": tool_type,
                "function": {
                    "name": tool_name,
                    "arguments": tool_json_args,
                },
            },
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": None,
            },
        ]

        if self._last_signature == signature:
            if self.stream_handler:
                self.stream_handler("\n")
                self.stream_handler(f"Skipping repeated tool call: {tool_name}\n")
            messages[-1]["content"] = f"Skipped repeated tool call: {tool_name}"
            return messages

        try:
            tool_args = json.loads(tool_json_args) if tool_json_args else {}
            if context is not None:
                tool_args["context"] = context
            result = tool(**tool_args)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error executing tool %s", tool_name)
            result = f"Error executing tool {tool_name}: {exc}"

        self._last_signature = signature

        if isinstance(result, list):
            messages[-1]["content"] = result
        else:
            messages[-1]["content"] = json.dumps(result, cls=CustomJsonEncoder)

        if self.stream_handler:
            self.stream_handler("\n")
            self.stream_handler(f"Tool {tool_name} execution completed.\n")

        return messages
