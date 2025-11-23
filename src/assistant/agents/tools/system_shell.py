import os
import logging
import subprocess
from assistant.utils.cli.executor import (
    execute_command_realtime_combined,
    execute_command_interactive,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

debug = os.getenv("FSC_ASSISTANT_DEBUG", "false").lower() == "true"

def run_shell_command(command_string: str, interactive: bool = False, timeout: int = None) -> str:
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
        timeout: Optional timeout in seconds for command execution. 
                If None (default), no timeout is applied.

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

        Commands with timeout:
        >>> output = run_shell_command("sleep 10", timeout=5)  # Will timeout

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
        - When timeout is specified, commands that exceed the limit will raise TimeoutExpired
    """
    # Validate input parameters
    if not isinstance(command_string, str):
        raise TypeError("command_string must be a string")
    
    if not isinstance(interactive, bool):
        raise TypeError("interactive must be a boolean")
        
    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ValueError("timeout must be a positive integer or None")

    # Log command execution start
    logger.debug(f"Starting command execution: {command_string}")
    
    try:
        if interactive:
            logger.debug(f"Running command in interactive mode: {command_string}")
            exit_code = execute_command_interactive(
                command_string, shell=True, env=os.environ
            )
            return f"Command exited with code: {exit_code}"
        else:
            logger.debug(f"Running command in non-interactive mode: {command_string}")
            
            # Handle timeout for non-interactive mode using subprocess.run
            if timeout is not None:
                try:
                    result = subprocess.run(
                        command_string,
                        shell=True,
                        env=os.environ,
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    logger.debug(f"Command completed successfully with exit code: {result.returncode}")
                    # Return combined stdout and stderr, or just stdout if no stderr
                    output = result.stdout + result.stderr if result.stderr else result.stdout
                    if debug is True:
                        print(">>>>>>>>>>> timeout Command Output Start >>>>>>>>>>>")
                        print(output)
                        print("<<<<<<<<<<< timeout Command Output End <<<<<<<<<<")
                    return output
                except subprocess.TimeoutExpired as e:
                    error_msg = f"Command timed out after {timeout} seconds. Command: {command_string}"
                    logger.error(error_msg)
                    # Re-raise the TimeoutError directly to maintain proper exception type
                    raise TimeoutError(error_msg) from e
            else:
                # Use existing implementation for backward compatibility
                exit_code, result = execute_command_realtime_combined(
                    command_string, shell=True, env=os.environ
                )
                if debug is True:
                    print(">>>>>>>>>>> Command Output Start >>>>>>>>>>>")
                    print(result)
                    print("<<<<<<<<<<< Command Output End <<<<<<<<<<")
                return result
                
    except FileNotFoundError as e:
        error_msg = f"Command not found: {command_string}. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
        
    except PermissionError as e:
        error_msg = f"Permission denied executing command: {command_string}. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
        
    except subprocess.SubprocessError as e:
        error_msg = f"Subprocess execution failed for command: {command_string}. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
        
    except TimeoutError:
        # Re-raise TimeoutError directly to maintain proper exception type
        raise
        
    except Exception as e:
        error_msg = f"Unexpected error executing command: {command_string}. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e