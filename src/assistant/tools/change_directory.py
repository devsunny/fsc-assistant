"""
Change Directory Tool for FSC Assistant

This tool allows the assistant to change the working directory 
within the agent's execution environment.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class ChangeDirectoryTool(BaseTool):
    """A tool that enables changing the current working directory."""
    
    name = "change_directory"
    description = "Change the current working directory to a specified path"
    parameters = {
        "path": {
            "type": "string",
            "description": "The directory path to change to. Can be absolute or relative.",
            "required": True
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the change directory command.
        
        Parameters:
            **kwargs: 
                path (str): The directory path to change to
            
        Returns:
            dict: Execution result with status and message
        """
        try:
            # Get the target path from parameters
            target_path = kwargs.get("path")
            
            if not target_path:
                return {
                    "success": False,
                    "error": "No path provided",
                    "message": "Please provide a directory path to change to"
                }
                
            # Resolve the path (handles relative paths)
            resolved_path = Path(target_path).resolve()
            
            # Check if path exists
            if not resolved_path.exists():
                return {
                    "success": False,
                    "error": "Path does not exist",
                    "message": f"Directory '{target_path}' does not exist"
                }
                
            # Check if it's actually a directory
            if not resolved_path.is_dir():
                return {
                    "success": False,
                    "error": "Not a directory",
                    "message": f"'{target_path}' is not a directory"
                }
            
            # Change the working directory
            original_cwd = os.getcwd()
            os.chdir(resolved_path)
            
            return {
                "success": True,
                "message": f"Successfully changed directory to '{resolved_path}'",
                "original_directory": original_cwd,
                "new_directory": str(resolved_path),
                "working_directory": os.getcwd()
            }
            
        except PermissionError:
            return {
                "success": False,
                "error": "Permission denied",
                "message": f"Permission denied to access directory '{target_path}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Directory change failed",
                "message": f"Failed to change directory: {str(e)}"
            }


# Tool registration for automatic discovery
TOOL_REGISTRY = [ChangeDirectoryTool]