import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from assistant.utils.cli.executor import (
    execute_command_interactive,
    execute_command_realtime_combined,
)
from assistant.utils.llm.img_utils import to_multipart_message_content
from assistant.utils.path import find_spec_file, get_project_root

logger = logging.getLogger(__name__)


def run_shell_command(command_string: str, interactive: bool = False) -> str:
    """
    Runs a shell command on the host system.

    This function supports two execution modes:

    1. **Non-interactive mode (default)**: Captures and returns command output.
       Use this for commands that don't require user input (ls, grep, cat, etc.)

    2. **Interactive mode**: Allows direct user input to the command.
       Use this for commands that require user interaction (vim, python REPL, less, etc.)

    Args:
        command_string: The shell command to execute
        interactive: If True, runs in interactive mode allowing user input.
                    If False (default), captures and returns output.

    Returns:
        str: For non-interactive mode, returns the captured command output.
             For interactive mode, returns a message with the exit code.

    Examples:
        Non-interactive commands (default behavior):
        >>> output = run_shell_command("ls -la")
        >>> output = run_shell_command("grep 'pattern' file.txt")
        >>> output = run_shell_command("cat README.md")

        Interactive commands (requires interactive=True):
        >>> run_shell_command("vim config.py", interactive=True)
        >>> run_shell_command("python3", interactive=True)  # Start Python REPL
        >>> run_shell_command("less large_file.log", interactive=True)
        >>> run_shell_command("nano README.md", interactive=True)

    Interactive Mode Use Cases:
        - Text editors: vim, nano, emacs
        - REPLs: python, python3, node, irb, ipython
        - Pagers: less, more
        - Debuggers: pdb, gdb
        - Interactive installers or configuration tools

    Notes:
        - Interactive mode inherits stdin/stdout/stderr for full terminal control
        - Interactive mode does not capture output (it goes directly to terminal)
        - Non-interactive mode captures both stdout and stderr
        - Default behavior (interactive=False) maintains backward compatibility
    """
    if interactive:
        logger.debug(f"Running command in interactive mode: {command_string}")
        exit_code = execute_command_interactive(
            command_string, shell=True, env=os.environ
        )
        return f"Command exited with code: {exit_code}"
    else:
        logger.debug(f"Running command in non-interactive mode: {command_string}")
        exit_code, result = execute_command_realtime_combined(
            command_string, shell=True, env=os.environ
        )
        return result


def get_current_local_time() -> str:
    """
    Get the current local date and time with timezone information.

    This function provides AI assistants with temporal awareness by returning
    the current date and time in multiple formats. This enables time-sensitive
    responses, accurate timestamp generation, and understanding of temporal
    context in user queries.

    Returns:
        str: Current local time in multiple formats:
             - ISO 8601 format with timezone offset
             - Timezone name and UTC offset
             - Human-readable format with day, date, and time

    Examples:
        Get current time information:
        >>> time_info = get_current_local_time()
        >>> print(time_info)
        Current local time: 2024-11-07T14:30:45.123456-05:00
        Timezone: EST (UTC-05:00)
        Human readable: Thursday, November 7, 2024 at 2:30:45 PM

        Use for timestamp generation:
        >>> time_info = get_current_local_time()
        >>> # Extract ISO format for logs
        >>> iso_time = time_info.split('\\n')[0].split(': ')[1]

        Use for temporal context:
        >>> time_info = get_current_local_time()
        >>> # AI can understand "today" means the date shown
        >>> if "Thursday" in time_info:
        ...     print("Today is Thursday")

    Notes:
        - Uses Python standard library only (no external dependencies)
        - Automatically detects local timezone
        - Handles Daylight Saving Time (DST) correctly
        - Executes in <10ms (no I/O or network calls)
        - Works consistently across all platforms (Linux, macOS, Windows)
        - Returns timezone-aware datetime information
    """
    try:
        # Get current time in local timezone
        now = datetime.now(tz=timezone.utc).astimezone()

        # Format ISO 8601 with timezone
        iso_format = now.isoformat()

        # Get timezone name and offset
        tz_name = now.strftime("%Z")
        tz_offset = now.strftime("%z")
        # Format offset as UTC±HH:MM
        tz_offset_formatted = f"{tz_offset[:3]}:{tz_offset[3:]}"

        # Human-readable format
        human_format = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")

        return (
            f"Current local time: {iso_format}\n"
            f"Timezone: {tz_name} (UTC{tz_offset_formatted})\n"
            f"Human readable: {human_format}"
        )
    except Exception as e:
        logger.exception("Error getting current time")
        return f"Error: Failed to get current time - {str(e)}"


def load_image_files(image_filepaths: List[str]) -> str:
    """load multiple image files from disk"""
    content = to_multipart_message_content(*image_filepaths)
    logger.info(f"Loaded {len(image_filepaths)} image files from disk.")
    return content


def spec_file_finder(spec_filename: str) -> str:
    """search spec file in the current project folder"""
    file_path = find_spec_file(get_project_root(Path.cwd()), spec_filename)
    return str(file_path.resolve())


# def get_spec_folder() -> str:
#     """find specification file folder in current project"""
#     file_path =  find_spec_folder( get_project_root(Path.cwd()))
#     return str(file_path.resolve())


def get_current_project_folder() -> str:
    """get current project root directory"""
    file_path = get_project_root(Path.cwd())
    return str(file_path.resolve())


def list_file_in_current_project() -> str:
    """list all files in current project"""
    files = []
    proj_root = get_project_root()
    for file_path in proj_root.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            files.append(str(proj_root.relative_to(file_path)))
    return "\n".join(files)


def save_text_file_to_disk(path: str, content: str) -> str:
    """Save text CONTENT to a file at PATH (create directories if needed). Returns the absolute path."""
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Saved to {p}"
    except Exception as e:
        return f"Failed to save file: {e!r}"


def load_text_file_from_disk(path: str) -> str:
    """Load and return the text contents of the file at PATH."""
    try:
        p = Path(path).expanduser().absolute()
        if not p.exists():
            return f"File not found: {p}"
        # Basic guard against very large files in CLI
        if p.stat().st_size > 5 * 1024 * 1024:
            return f"File too large to display (>5MB): {p}"
        data = p.read_text(encoding="utf-8", errors="ignore")
        return data
    except Exception as e:
        return f"Failed to load file: {e}"
