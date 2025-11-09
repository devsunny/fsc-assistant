import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import BaseTool from the new location
from .base_tool import BaseTool


def load_text_file_from_disk(path: str) -> str:
    """
    Load and return the text contents of the file at PATH.
    
    Parameters
    ----------
    path : str
        The path to the file to read
        
    Returns
    -------
    str
        The content of the file as a string
        
    Raises
    ------
    FileNotFoundError
        If the file does not exist
    """
    logger.info(f"Loading text file: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_text_file_to_disk(path: str, content: str) -> str:
    """
    Save text CONTENT to a file at PATH (create directories if needed). 
    Returns the absolute path.
    
    Parameters
    ----------
    path : str
        The path where the file should be saved
    content : str
        The text content to write
        
    Returns
    -------
    str
        The absolute path of the saved file
    """
    logger.info(f"Saving text file: {path}")
    
    abs_path = Path(path).resolve()
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return str(abs_path)


# Tool class that extends BaseTool
class LoadTextFileFromDiskTool(BaseTool):
    """A tool for loading text files from disk."""
    
    name = "load_text_file_from_disk"
    description = "Load and return the text contents of a file at PATH"
    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to read",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute loading a text file.
        
        Parameters:
            **kwargs: 
                path (str): The path to the file to read
                
        Returns:
            dict: File content or error information
        """
        try:
            path = kwargs.get("path")
            
            if not path:
                return {
                    "success": False,
                    "error": "No path provided",
                    "message": "Please provide a file path"
                }
                
            content = load_text_file_from_disk(path)
            
            return {
                "success": True,
                "content": content,
                "path": path
            }
        except Exception as e:
            return {
                "success": False,
                "error": "File loading failed",
                "message": f"Failed to load file: {str(e)}"
            }


# Tool class that extends BaseTool  
class SaveTextFileToDiskTool(BaseTool):
    """A tool for saving text files to disk."""
    
    name = "save_text_file_to_disk"
    description = "Save text content to a file at PATH (create directories if needed)"
    parameters = {
        "path": {
            "type": "string",
            "description": "The path where the file should be saved",
            "required": True
        },
        "content": {
            "type": "string", 
            "description": "The text content to write",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute saving a text file.
        
        Parameters:
            **kwargs: 
                path (str): The path where the file should be saved
                content (str): The text content to write
                
        Returns:
            dict: Success status and absolute path of saved file
        """
        try:
            path = kwargs.get("path")
            content = kwargs.get("content")
            
            if not path or not content:
                return {
                    "success": False,
                    "error": "Missing required parameters",
                    "message": "Please provide both path and content"
                }
                
            abs_path = save_text_file_to_disk(path, content)
            
            return {
                "success": True,
                "path": abs_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": "File saving failed",
                "message": f"Failed to save file: {str(e)}"
            }


# Tool registry for automatic discovery
TOOL_REGISTRY = [
    LoadTextFileFromDiskTool,
    SaveTextFileToDiskTool
]