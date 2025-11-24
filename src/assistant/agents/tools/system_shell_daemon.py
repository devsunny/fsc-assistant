import os
import re
import signal
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, List
from assistant.utils.cli.executor import (
    execute_command_realtime_combined,
    execute_command_interactive,
)

# Global registry to track daemon processes
_daemon_processes: Dict[int, dict] = {}
_process_lock = threading.Lock()


def _cleanup_terminated_processes():
    """Clean up terminated processes from the registry."""
    global _daemon_processes
    with _process_lock:
        current_time = time.time()
        # Simple cleanup - remove processes that have been terminated for more than 5 minutes
        expired_pids = [
            pid
            for pid, info in _daemon_processes.items()
            if info.get("status") == "terminated"
            and (
                current_time
                - (
                    info.get("end_time", current_time).timestamp()
                    if hasattr(info.get("end_time"), "timestamp")
                    else info.get("end_time", current_time)
                )
            )
            > 300
        ]
        for pid in expired_pids:
            del _daemon_processes[pid]


def run_shell_command_daemon(command_string: str, timeout: int = 180) -> dict:
    """
    Runs a shell command in daemon mode (background process).

    This function launches the specified command as a background process that
    runs independently of the main execution thread. The process can be managed
    and terminated using provided management functions.

    Args:
        command_string: The shell command to execute
        timeout: Optional timeout in seconds for command execution

    Returns:
        dict: Process information including PID, status, start time, and command

    Examples:
        >>> # Start a long-running process in daemon mode
        >>> result = run_shell_command_daemon("sleep 3600")
        >>> print(f"Started daemon with PID: {result['pid']}")

        >>> # Start with timeout
        >>> result = run_shell_command_daemon("ping google.com", timeout=10)
    """

    # Validate input parameters
    if not isinstance(command_string, str):
        raise TypeError("command_string must be a string")

    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ValueError("timeout must be a positive integer or None")

    try:
        # Create subprocess in daemon mode
        process = subprocess.Popen(
            command_string,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid,  # Create new process group to isolate from terminal signals
        )

        pid = process.pid

        # Register the process in our registry
        process_info = {
            "pid": pid,
            "command": command_string,
            "start_time": datetime.now(),
            "status": "running",
            "timeout": timeout,
        }

        with _process_lock:
            _daemon_processes[pid] = process_info

        # If a timeout is specified, set up automatic termination
        if timeout is not None:

            def kill_after_timeout():
                time.sleep(timeout)
                try:
                    # Check if process still exists and terminate it
                    with _process_lock:
                        if (
                            pid in _daemon_processes
                            and _daemon_processes[pid]["status"] == "running"
                        ):
                            os.killpg(os.getpgid(pid), signal.SIGTERM)
                            _daemon_processes[pid]["status"] = "terminated"
                            _daemon_processes[pid]["end_time"] = datetime.now()
                except Exception:
                    # Process might have already terminated
                    pass

            timeout_thread = threading.Thread(target=kill_after_timeout, daemon=True)
            timeout_thread.start()

        return {
            "pid": pid,
            "status": "running",
            "start_time": process_info["start_time"],
            "command": command_string,
        }

    except Exception as e:
        error_msg = f"Failed to start daemon process for command: {command_string}. Error: {str(e)}"
        raise RuntimeError(error_msg) from e


def list_daemon_processes() -> List[dict]:
    """
    List all currently running daemon processes.

    Returns:
        List[dict]: Information about each running daemon process
    """
    _cleanup_terminated_processes()

    with _process_lock:
        # Return copy of current processes to avoid external modification
        return [
            {
                "pid": pid,
                "command": info["command"],
                "start_time": info["start_time"],
                "status": info["status"],
            }
            for pid, info in _daemon_processes.items()
            if info.get("status") == "running"
        ]


def terminate_daemon_process(pid: int) -> bool:
    """
    Terminate a specific daemon process by PID.

    Args:
        pid (int): The process ID to terminate

    Returns:
        bool: True if termination was successful, False otherwise
    """
    try:
        with _process_lock:
            if pid not in _daemon_processes:
                return False

            # Mark as terminating first
            _daemon_processes[pid]["status"] = "terminating"

        # Send SIGTERM to the process group (to handle child processes)
        os.killpg(os.getpgid(pid), signal.SIGTERM)

        with _process_lock:
            if pid in _daemon_processes:
                _daemon_processes[pid]["status"] = "terminated"
                _daemon_processes[pid]["end_time"] = datetime.now()

        return True

    except Exception as e:
        # If process already terminated or doesn't exist, that's okay
        with _process_lock:
            if pid in _daemon_processes:
                _daemon_processes[pid]["status"] = "terminated"
                _daemon_processes[pid]["end_time"] = datetime.now()
        return False


def check_daemon_status(pid: int) -> dict:
    """
    Check status of a daemon process.

    Args:
        pid (int): The process ID to check

    Returns:
        dict: Status information about the process
    """
    with _process_lock:
        if pid not in _daemon_processes:
            return {"status": "not_found"}

        info = _daemon_processes[pid]
        # Check actual process status
        try:
            os.kill(pid, 0)  # This will raise OSError if process doesn't exist
            # Process exists, check if it's still running or terminated
            if info["status"] == "running":
                return {
                    "pid": pid,
                    "command": info["command"],
                    "start_time": info["start_time"],
                    "status": "running",
                }
        except OSError:
            # Process doesn't exist, update registry
            _daemon_processes[pid]["status"] = "terminated"
            _daemon_processes[pid]["end_time"] = datetime.now()

        return {
            "pid": pid,
            "command": info["command"],
            "start_time": info["start_time"],
        }


def is_frontend_dev_server(command: str) -> bool:
    """
    Detects if a shell command string is likely starting a frontend dev server.
    """
    # Normalize command to lowercase
    cmd = command.lower()

    # Common frontend dev server keywords
    patterns = [
        r"npm\s+run\s+(dev|start|serve)",
        r"yarn\s+(dev|start|serve)",
        r"pnpm\s+run\s+(dev|start|serve)",
        r"next\s+dev",
        r"vite\s+serve?",
        r"nuxt\s+(dev|start)",
        r"react-scripts\s+start",
        r"vue-cli-service\s+serve",
        r"ng\s+serve",  # Angular
    ]

    return any(re.search(p, cmd) for p in patterns)


def run_shell_command(
    command_string: str,
    interactive: bool = False,
    timeout: int = 180,
    daemon_mode: bool = False,
) -> str:
    """
    Runs a shell command on the host system.
    """

    # Validate input parameters
    if not isinstance(command_string, str):
        raise TypeError("command_string must be a string")

    if not isinstance(interactive, bool):
        raise TypeError("interactive must be a boolean")

    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ValueError("timeout must be a positive integer or None")

    if not isinstance(daemon_mode, bool):
        raise TypeError("daemon_mode must be a boolean")

    if is_frontend_dev_server(command_string):
        daemon_mode = True

    # Handle daemon mode
    if daemon_mode:
        result = run_shell_command_daemon(command_string, timeout)
        return f"Started daemon process with PID: {result['pid']}"

    # Log command execution start
    import logging

    logger = logging.getLogger(__name__)
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
                        timeout=timeout,
                    )
                    logger.debug(
                        f"Command completed successfully with exit code: {result.returncode}"
                    )
                    # Return combined stdout and stderr, or just stdout if no stderr
                    output = (
                        result.stdout + result.stderr
                        if result.stderr
                        else result.stdout
                    )
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
                return result

    except FileNotFoundError as e:
        error_msg = f"Command not found: {command_string}. Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    except PermissionError as e:
        error_msg = (
            f"Permission denied executing command: {command_string}. Error: {str(e)}"
        )
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
        error_msg = (
            f"Unexpected error executing command: {command_string}. Error: {str(e)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


# Signal handling for graceful shutdown (optional, can be used by calling code)
def setup_signal_handlers():
    """
    Setup signal handlers to properly terminate daemon processes.

    This function should be called once during application startup to ensure
    proper cleanup when the main process receives termination signals.
    """

    def signal_handler(signum, frame):
        # Terminate all running daemon processes
        with _process_lock:
            pids_to_terminate = [
                pid
                for pid, info in _daemon_processes.items()
                if info.get("status") == "running"
            ]

        for pid in pids_to_terminate:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except Exception:
                pass  # Process might have already terminated

        # Exit the application
        exit(0)

    # Register handlers for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Export functions to make them available as tools
__all__ = [
    "run_shell_command_daemon",
    "list_daemon_processes",
    "terminate_daemon_process",
    "check_daemon_status",
    "run_shell_command",
    "setup_signal_handlers",
]
