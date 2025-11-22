import os
import logging

logger = logging.getLogger(__name__)


def change_working_directory(target_path: str) -> str:
    """
    Change the current working directory of the current process.    
    """
    # Validate input parameter
    if not isinstance(target_path, str):
        raise TypeError("target_path must be a string")
    
    if not target_path.strip():
        raise ValueError("target_path cannot be empty")

    try:
        # Resolve the path to absolute form for consistency
        abs_target_path = os.path.abspath(target_path)
        
        # Check if the path exists and is a directory
        if not os.path.exists(abs_target_path):
            return f"Error: Directory '{abs_target_path}' does not exist."
            
        if not os.path.isdir(abs_target_path):
            return f"Error: Path '{abs_target_path}' is not a directory."
        
        # Check permissions - try to access the directory
        if not os.access(abs_target_path, os.R_OK | os.X_OK):
            return f"Error: Permission denied accessing directory '{abs_target_path}'."
            
        # Change working directory
        old_cwd = os.getcwd()
        os.chdir(abs_target_path)
        
        logger.debug(f"Changed working directory from {old_cwd} to {abs_target_path}")
        return f"Successfully changed working directory to {abs_target_path}"
        
    except Exception as e:
        error_msg = f"Failed to change working directory to '{target_path}'. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e