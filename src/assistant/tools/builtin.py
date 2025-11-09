import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from assistant.utils.cli.executor import (
    execute_command_interactive,
    execute_command_realtime_combined,
)
from assistant.utils.llm.img_utils import to_multipart_message_content
from assistant.utils.path import find_spec_file, get_project_root

logger = logging.getLogger(__name__)


# Import BaseTool from the new location
from .base_tool import BaseTool


def run_shell_command(command_string: str, interactive: bool = False) -> str:
    """
    Runs a shell command on the host system.

    This function supports two execution modes:
    - Non-interactive (default): Executes and returns output as string
    - Interactive: Spawns an interactive terminal session

    Parameters
    ----------
    command_string : str
        The shell command to execute
    interactive : bool, optional
        If True, runs in interactive mode allowing user input.

    Returns
    -------
    str
        Output of the executed command or empty string if interactive=True
    """
    logger.info(f"Running shell command: {command_string}")
    
    if interactive:
        return execute_command_interactive(command_string)
    else:
        return execute_command_realtime_combined(command_string)


def get_current_local_time() -> str:
    """Get the current local date and time with timezone information."""
    now = datetime.now(timezone.utc).astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


# Tool class that extends BaseTool
class RunShellCommandTool(BaseTool):
    """A tool for running shell commands."""
    
    name = "run_shell_command"
    description = "Run a shell command on the host system"
    parameters = {
        "command_string": {
            "type": "string",
            "description": "The shell command to execute",
            "required": True
        },
        "interactive": {
            "type": "boolean", 
            "description": "If True, runs in interactive mode allowing user input",
            "required": False,
            "default": False
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute the shell command.
        
        Parameters:
            **kwargs: 
                command_string (str): The shell command to execute
                interactive (bool): If True, runs in interactive mode
                
        Returns:
            dict: Execution result with status and output
        """
        try:
            command_string = kwargs.get("command_string")
            interactive = kwargs.get("interactive", False)
            
            if not command_string:
                return {
                    "success": False,
                    "error": "No command provided",
                    "message": "Please provide a shell command to execute"
                }
                
            output = run_shell_command(command_string, interactive)
            
            return {
                "success": True,
                "output": output,
                "command": command_string
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Command execution failed",
                "message": f"Failed to execute command: {str(e)}"
            }


# Tool class that extends BaseTool  
class GetCurrentLocalTimeTool(BaseTool):
    """A tool for getting current local time."""
    
    name = "get_current_local_time"
    description = "Get the current local date and time with timezone information"
    parameters = {}

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute getting current local time.
        
        Returns:
            dict: Current time information
        """
        try:
            current_time = get_current_local_time()
            
            return {
                "success": True,
                "time": current_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Time retrieval failed",
                "message": f"Failed to retrieve time: {str(e)}"
            }


# Tool registry for automatic discovery
TOOL_REGISTRY = [
    RunShellCommandTool,
    GetCurrentLocalTimeTool
]