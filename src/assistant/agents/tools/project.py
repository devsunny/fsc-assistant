import logging
from pathlib import Path
from assistant.utils.path import get_project_root

logger = logging.getLogger(__name__)


def get_current_project_root_folder() -> str:
    """get current project root directory"""
    file_path = get_project_root(Path.cwd())
    return str(file_path.resolve())


def list_files_in_current_project() -> str:
    """list all files in current project"""
    files = []
    proj_root = get_project_root()
    for file_path in proj_root.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            files.append(str(proj_root.relative_to(file_path)))
    return "\n".join(files)
