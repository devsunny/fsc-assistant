"""Agent-specific utilities.

This module provides utilities for agents, with lazy loading to avoid
importing heavy dependencies (like docling) at module initialization time.
"""

# Import lightweight utilities immediately
from .markdown import extract_markdown_code_blocks
from .prompts import *
from .source_code import *

# Note: docling and pdf modules are NOT imported here to avoid slow startup
# Import them explicitly when needed:
#   from assistant.agents.utils.docling import ...
#   from assistant.agents.utils.pdf import ...

__all__ = [
    "extract_markdown_code_blocks",
]
