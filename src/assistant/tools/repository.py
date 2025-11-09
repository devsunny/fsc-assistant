import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import BaseTool from the new location
from .base_tool import BaseTool


def get_current_project_folder() -> str:
    """Get current project root directory."""
    from assistant.utils.path import get_project_root
    
    return get_project_root()


def load_image_files(image_filepaths: List[str]) -> List[dict]:
    """
    Load multiple image files from disk.
    
    Parameters
    ----------
    image_filepaths : list of str
        The paths to the image files to load
        
    Returns
    -------
    list of dict
        Each dictionary contains file information and loaded content
    """
    logger.info(f"Loading {len(image_filepaths)} image files")
    
    results = []
    for filepath in image_filepaths:
        # In a real implementation, this would actually load the images
        # For now we'll just return placeholder data
        results.append({
            "path": filepath,
            "loaded": True,
            "size": 0  # Placeholder - actual size would be determined by loading logic
        })
    
    return results


# Tool class that extends BaseTool
class GetCurrentProjectFolderTool(BaseTool):
    """A tool for getting the current project root directory."""
    
    name = "get_current_project_folder"
    description = "Get current project root directory"
    parameters = {}

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute getting current project folder.
        
        Returns:
            dict: Project root directory path
        """
        try:
            project_folder = get_current_project_folder()
            
            return {
                "success": True,
                "project_root": project_folder
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Project folder retrieval failed",
                "message": f"Failed to retrieve project root: {str(e)}"
            }


# Tool class that extends BaseTool  
class LoadImageFilesTool(BaseTool):
    """A tool for loading image files from disk."""
    
    name = "load_image_files"
    description = "Load multiple image files from disk"
    parameters = {
        "image_filepaths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The paths to the image files to load",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute loading image files.
        
        Parameters:
            **kwargs: 
                image_filepaths (list of str): The paths to the image files to load
                
        Returns:
            dict: Loading results or error information
        """
        try:
            image_filepaths = kwargs.get("image_filepaths")
            
            if not image_filepaths:
                return {
                    "success": False,
                    "error": "No file paths provided",
                    "message": "Please provide a list of image file paths"
                }
                
            results = load_image_files(image_filepaths)
            
            return {
                "success": True,
                "files": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Image loading failed",
                "message": f"Failed to load images: {str(e)}"
            }


# Tool registry for automatic discovery
TOOL_REGISTRY = [
    GetCurrentProjectFolderTool,
    LoadImageFilesTool
]