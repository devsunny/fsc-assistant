import logging
import os
from typing import Any, Optional, List  
import httpx  
from pathlib import Path
from fsc.config import ConfigManager
from .realtime_command_executor import execute_system_command_realtime 
from .images_utils import to_llm_message_content
from .document_utils import read_document

logger = logging.getLogger(__name__)




def download_file_via_http(url: str, timeout: int = 10) -> str:
    """Download a file from a URL and return its content as a string."""
    try:        
        return read_document(url)
    except Exception as e:
        return f"Failed to download file from {url}: {e!r}"


def get_project_root_dir(start_path:Optional[Path]=None)->Path:
    """Get the root directory of the project."""
    start_path = start_path or Path.cwd()
    for parent in start_path.parents:
        if ((parent / ".git").exists() 
            or (parent / ".github").exists()
            or (parent / "pyproject.toml").exists()):
            return parent
    return start_path


def run_shell_command(command_string:str)->str:
    """Runs a shell command on the host system and captures its output."""
    exit_code, result = execute_system_command_realtime(command_string, shell=True, env=os.environ)
    return result       
    

def load_image_files(image_filepaths:List[str]) -> str:
    """load multiple image files from disk"""  
    content = to_llm_message_content(*image_filepaths)   
    logger.info(f"Loaded {len(image_filepaths)} image files from disk.") 
    return content

def list_file_in_current_project() -> str:
    """list all files in current project"""
    files = []
    proj_root = get_project_root_dir()
    for file_path in proj_root.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."): 
            files.append(str(proj_root.relative_to(file_path))) 
    return "\n".join(files)


def save_file_to_disk(path: str, content: str) -> str:
    """Save text CONTENT to a file at PATH (create directories if needed). Returns the absolute path."""
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Saved to {p}"
    except Exception as e:
        return f"Failed to save file: {e!r}"


def load_file_from_disk(path: str) -> str:
    """Load and return the text contents of the file at PATH."""       
    try:
        p = Path(path).expanduser().absolute()
        if not p.exists():
            return f"File not found: {p}"
        # Basic guard against very large files in CLI
        if path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".pdf", ".mp4", ".mp3", ".avi", ".mov", ".mkv", ".docx", ".xlsx", ".pptx"]:
            return read_document(p)
        
        if p.stat().st_size > 5 * 1024 * 1024:
            return f"File too large to display (>5MB): {p}"
        data = p.read_text(encoding="utf-8", errors="ignore")
        return data
    except Exception as e:
        return f"Failed to load file: {e}"
    
    
def list_available_models() -> str:
    """List available LLM models (stub function)."""
    config = ConfigManager()
    available_models = config.get("llm.models", [])
    if not available_models:
        return "No LLM models configured."
    return "\n".join(available_models)

BUILTIN_TOOLS = [read_document,
                 get_project_root_dir, 
                 run_shell_command, 
                 load_image_files, 
                 list_file_in_current_project, 
                 save_file_to_disk, 
                 load_file_from_disk, 
                 download_file_via_http, 
                 list_available_models]

def get_builtin_tools() -> List[Any]:
    """Return the list of built-in tools."""
    return BUILTIN_TOOLS