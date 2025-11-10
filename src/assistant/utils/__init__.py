"""General utilities and helper functions."""

# Explicit imports for better performance and clarity
from .json import CustomJsonEncoder, extract_json_from_text
from .path import get_project_root, get_relative_path


__all__ = [
    # JSON utilities
    "CustomJsonEncoder",
    "extract_json_from_text",
    # Path utilities
    "get_project_root",
    "get_relative_path",
]
