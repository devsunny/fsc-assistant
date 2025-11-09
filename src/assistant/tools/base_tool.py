"""
Base Tool Class for FSC Assistant

This module defines the base class for all tools that can be used 
by the FSC Assistant to perform actions in the execution environment.
"""

from typing import Dict, Any, Optional
import inspect


class BaseTool:
    """Base class for all assistant tools."""
    
    # These attributes should be overridden by subclasses
    name: str = "base_tool"
    description: str = "A base tool implementation"
    parameters: Dict[str, Any] = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool with optional configuration.
        
        Parameters:
            config (dict): Configuration options for the tool
        """
        self.config = config or {}
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        This method should be overridden by subclasses to implement 
        specific tool functionality.
        
        Parameters:
            **kwargs: Tool-specific parameters
            
        Returns:
            dict: Execution result containing success status and message
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get information about this tool including its name, description, 
        and expected parameters.
        
        Returns:
            dict: Tool metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "signature": inspect.signature(self.execute)
        }
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate that the provided parameters match what the tool expects.
        
        Parameters:
            params (dict): Parameters to validate
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        # Check required parameters
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False) and param_name not in params:
                return False
                
        return True