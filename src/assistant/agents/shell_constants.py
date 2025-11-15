"""
Constants and patterns for the Kara Code shell.

This module contains all magic strings, file extensions, command patterns,
and UI messages used by the AgenticShell class.
"""

import re
from typing import List, Pattern

# Document file extensions
DOCUMENT_EXTENSIONS: List[str] = [
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".csv",
    ".pptx",
    ".jpg",
    ".png",
    ".jpeg",
    ".tiff",
    ".bmp",
]

# Keywords for document detection
DOCUMENT_ANALYSIS_KEYWORDS: List[str] = [
    "explain",
    "summarize",
    "what is",
    "describe",
]

DOCUMENT_EXTRACTION_KEYWORDS: List[str] = [
    "extract",
]

# Command lists
EXIT_COMMANDS: List[str] = ["exit", "quit", "q", "bye"]
HELP_COMMANDS: List[str] = ["help", "?"]

# Command patterns (compiled regex)
PATTERN_CLEAR_HISTORY: Pattern = re.compile(r"^clear\s*history$")
PATTERN_NEW_CHAT: Pattern = re.compile(r"new(\s*chat)?$")
PATTERN_SAVE_HISTORY: Pattern = re.compile(r"^save\s*history$")
PATTERN_SHOW_HISTORY: Pattern = re.compile(r"^show\s*history$")
PATTERN_MCP_STATUS: Pattern = re.compile(r"^mcp\s*status$")
PATTERN_ASK_AI: Pattern = re.compile(r"^ask\s*ai$")
PATTERN_ANALYZE: Pattern = re.compile(r"^analyze$")
# OpenSpec command prefixes
OPENSPEC_PROPOSAL_PREFIXES: List[str] = ["/openspec-proposal", "/openspec:proposal"]
OPENSPEC_APPLY_PREFIXES: List[str] = ["/openspec-apply", "/openspec:apply"]
OPENSPEC_ARCHIVE_PREFIXES: List[str] = ["/openspec-archive", "/openspec:archive"]

# OpenSpec prompt template filenames
OPENSPEC_PROPOSAL_TEMPLATE: str = "openspec-proposal.prompt.md"
OPENSPEC_APPLY_TEMPLATE: str = "openspec-apply.prompt.md"
OPENSPEC_ARCHIVE_TEMPLATE: str = "openspec-archive.prompt.md"

# UI Messages
MSG_GOODBYE: str = "[bold red]Goodbye![/bold red]"
MSG_COMMAND_SUCCESS: str = "command execute sucessfully"
MSG_COMMAND_FAILED: str = "command execution failed: status code {}"
MSG_NO_RESPONSE: str = "No response received"
MSG_USE_EXIT: str = "Use 'exit' or 'quit' to leave the shell"
MSG_NO_HISTORY: str = "No chat history found."
MSG_ASSISTANT_PREFIX: str = "[Asisstant]: "

# System prompts
DOCUMENT_ANALYSIS_SYSTEM_PROMPT: str = """You are a helpful assistant. Analyze and summarize or extract the document accurately and concisely. 
If document size is too large, please split it into multiple parts and process each part separately."""

# File paths
AGENTS_MD_FILENAME: str = "AGENTS.md"
PROMPTS_DIR: str = ".github/prompts"
