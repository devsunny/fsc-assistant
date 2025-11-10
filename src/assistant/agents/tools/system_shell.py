import os
import logging
from assistant.utils.cli.executor import (
    execute_command_realtime_combined,
    execute_command_interactive,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
