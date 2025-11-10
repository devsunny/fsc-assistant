#!/usr/bin/env python3
"""
Real-time System Command Executor
Execute system commands and print output in real-time as it's generated.
"""
import shlex
import subprocess
import sys
import threading
from typing import Callable, Optional, Tuple


def execute_command_realtime(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    timeout: Optional[int] = None,
    stdout_prefix: str = "",
    stderr_prefix: str = "[ERROR] ",
) -> int:
    """
    Execute a system command and print output in real-time.

    Args:
        command (str): The command to execute as a single line string
        shell (bool): Whether to execute through shell (default: False)
        cwd (str, optional): Working directory for command execution
        env (dict, optional): Environment variables for the command
        timeout (int, optional): Maximum time in seconds to wait
        stdout_prefix (str): Prefix for stdout lines (default: "")
        stderr_prefix (str): Prefix for stderr lines (default: "[ERROR] ")

    Returns:
        int: The exit code of the command (0 = success)

    Examples:
        >>> # Simple command with real-time output
        >>> code = execute_command_realtime("echo 'Hello World'")
        Hello World
        >>> print(f"Exit code: {code}")
        Exit code: 0

        >>> # Long-running command
        >>> code = execute_command_realtime("ping -c 5 google.com")
        PING google.com ...
        64 bytes from ...
        ...

        >>> # Command with error output
        >>> code = execute_command_realtime("ls /nonexistent")
        [ERROR] ls: cannot access '/nonexistent': No such file or directory
    """
    try:
        # Parse command into arguments if not using shell
        if not shell:
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        # Start the process
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            cwd=cwd,
            env=env,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )

        # Read stdout in real-time
        for line in process.stdout:
            print(f"{stdout_prefix}{line}", end="", flush=True)

        # Read stderr in real-time
        for line in process.stderr:
            print(f"{stderr_prefix}{line}", end="", flush=True)

        # Wait for process to complete
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"\n[TIMEOUT] Command exceeded {timeout} seconds and was terminated")
            return -1

        return process.returncode

    except FileNotFoundError:
        print(f"[ERROR] Command not found: {command.split()[0]}", file=sys.stderr)
        return -1

    except PermissionError:
        print(f"[ERROR] Permission denied executing: {command}", file=sys.stderr)
        return -1

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}", file=sys.stderr)
        return -1


def execute_command_realtime_combined(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    timeout: Optional[int] = None,
    prefix: str = "",
) -> Tuple[int, str]:
    """
    Execute command with real-time output and also capture all output.

    Args:
        command (str): The command to execute
        shell (bool): Whether to execute through shell
        cwd (str, optional): Working directory
        env (dict, optional): Environment variables
        timeout (int, optional): Maximum execution time
        prefix (str): Prefix for all output lines

    Returns:
        Tuple[int, str]: (exit_code, captured_output)

    Examples:
        >>> code, output = execute_command_realtime_combined("echo 'test'")
        test
        >>> print(f"Captured: {output.strip()}")
        Captured: test
    """
    try:
        if not shell:
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            shell=shell,
            cwd=cwd,
            env=env,
            bufsize=1,
            universal_newlines=True,
        )

        output_lines = []

        # Read and print output in real-time
        for line in process.stdout:
            print(f"{prefix}{line}", end="", flush=True)
            output_lines.append(line)

        # Wait for completion
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            timeout_msg = f"\n[TIMEOUT] Command exceeded {timeout} seconds\n"
            print(timeout_msg)
            output_lines.append(timeout_msg)
            return -1, "".join(output_lines)

        return process.returncode, "".join(output_lines)

    except Exception as e:
        error_msg = f"[ERROR] {str(e)}\n"
        print(error_msg, file=sys.stderr)
        return -1, error_msg


def execute_command_realtime_threaded(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    timeout: Optional[int] = None,
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[int, str, str]:
    """
    Execute command with real-time output using threads for stdout/stderr.
    This ensures stdout and stderr are printed immediately without blocking each other.

    Args:
        command (str): The command to execute
        shell (bool): Whether to execute through shell
        cwd (str, optional): Working directory
        env (dict, optional): Environment variables
        timeout (int, optional): Maximum execution time
        stdout_callback (callable, optional): Function to call for each stdout line
        stderr_callback (callable, optional): Function to call for each stderr line

    Returns:
        Tuple[int, str, str]: (exit_code, stdout_output, stderr_output)

    Examples:
        >>> def custom_handler(line):
        ...     print(f">>> {line}", end='')
        >>> code, out, err = execute_command_realtime_threaded(
        ...     "echo 'test'",
        ...     stdout_callback=custom_handler
        ... )
        >>> test
    """
    try:
        if not shell:
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            cwd=cwd,
            env=env,
            bufsize=1,
            universal_newlines=True,
        )

        stdout_lines = []
        stderr_lines = []

        def read_stdout():
            """Read stdout in a separate thread."""
            for line in process.stdout:
                stdout_lines.append(line)
                if stdout_callback:
                    stdout_callback(line)
                else:
                    print(line, end="", flush=True)

        def read_stderr():
            """Read stderr in a separate thread."""
            for line in process.stderr:
                stderr_lines.append(line)
                if stderr_callback:
                    stderr_callback(line)
                else:
                    print(f"[ERROR] {line}", end="", flush=True)

        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(target=read_stdout)
        stderr_thread = threading.Thread(target=read_stderr)

        stdout_thread.start()
        stderr_thread.start()

        # Wait for process to complete
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"\n[TIMEOUT] Command exceeded {timeout} seconds")
            return -1, "".join(stdout_lines), "".join(stderr_lines)

        # Wait for threads to finish reading
        stdout_thread.join()
        stderr_thread.join()

        return process.returncode, "".join(stdout_lines), "".join(stderr_lines)

    except Exception as e:
        error_msg = f"[ERROR] {str(e)}\n"
        print(error_msg, file=sys.stderr)
        return -1, "", error_msg


def execute_command_with_progress(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    show_command: bool = True,
) -> int:
    """
    Execute command with a nice progress display.

    Args:
        command (str): The command to execute
        shell (bool): Whether to execute through shell
        cwd (str, optional): Working directory
        env (dict, optional): Environment variables
        show_command (bool): Whether to show the command being executed

    Returns:
        int: Exit code

    Examples:
        >>> code = execute_command_with_progress("ls -la")
        ┌─────────────────────────────────────────
        │ Executing: ls -la
        └─────────────────────────────────────────
        total 48
        drwxr-xr-x  ...
        ┌─────────────────────────────────────────
        │ Exit code: 0 ✓
        └─────────────────────────────────────────
    """
    if show_command:
        print("┌" + "─" * 45)
        print(f"│ Executing: {command}")
        print("└" + "─" * 45)

    code = execute_command_realtime(command, shell=shell, cwd=cwd, env=env)

    if show_command:
        status = "✓" if code == 0 else "✗"
        print("┌" + "─" * 45)
        print(f"│ Exit code: {code} {status}")
        print("└" + "─" * 45)

    return code


def execute_command_interactive(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
) -> int:
    """
    Execute command interactively (allows user input to the command).

    Args:
        command (str): The command to execute
        shell (bool): Whether to execute through shell
        cwd (str, optional): Working directory
        env (dict, optional): Environment variables

    Returns:
        int: Exit code

    Examples:
        >>> # This allows interactive commands like vim, less, etc.
        >>> code = execute_command_interactive("python3")
        Python 3.x.x
        >>> print("Hello")
        Hello
        >>> exit()
    """
    try:
        if not shell:
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        # Run with inherited stdin/stdout/stderr for full interactivity
        process = subprocess.run(cmd_args, shell=shell, cwd=cwd, env=env)

        return process.returncode

    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        return -1


def stream_command_output(
    command: str,
    shell: bool = False,
    line_callback: Optional[Callable[[str, bool], None]] = None,
) -> int:
    """
    Stream command output with callback for each line.

    Args:
        command (str): The command to execute
        shell (bool): Whether to execute through shell
        line_callback (callable, optional): Function(line, is_stderr) called for each line

    Returns:
        int: Exit code

    Examples:
        >>> def process_line(line, is_stderr):
        ...     if is_stderr:
        ...         print(f"ERR: {line}", end='')
        ...     else:
        ...         print(f"OUT: {line}", end='')
        >>> code = stream_command_output("ls", line_callback=process_line)
    """

    def default_callback(line, is_stderr):
        if is_stderr:
            print(f"[STDERR] {line}", end="", flush=True)
        else:
            print(line, end="", flush=True)

    callback = line_callback or default_callback

    try:
        if not shell:
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            bufsize=1,
            universal_newlines=True,
        )

        def read_stream(stream, is_stderr):
            for line in stream:
                callback(line, is_stderr)

        # Create threads for stdout and stderr
        stdout_thread = threading.Thread(
            target=read_stream, args=(process.stdout, False)
        )
        stderr_thread = threading.Thread(
            target=read_stream, args=(process.stderr, True)
        )

        stdout_thread.start()
        stderr_thread.start()

        # Wait for completion
        process.wait()

        stdout_thread.join()
        stderr_thread.join()

        return process.returncode

    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        return -1


# Example usage and demonstrations
def main():
    """Demonstrate the real-time command executor functions."""
    print("=" * 70)
    print("Real-time System Command Executor - Examples")
    print("=" * 70)

    # Example 1: Simple command with real-time output
    print("\n1. Simple echo command:")
    print("-" * 50)
    code = execute_command_realtime("echo 'Hello, World!'")
    print(f"Exit code: {code}\n")

    # Example 2: Command with multiple lines of output
    print("\n2. List files with real-time output:")
    print("-" * 50)
    code = execute_command_realtime("ls -la")
    print(f"Exit code: {code}\n")

    # Example 3: Command that takes time (shows real-time nature)
    print("\n3. Command with delays (shows real-time output):")
    print("-" * 50)
    code = execute_command_realtime(
        "bash -c 'for i in 1 2 3; do echo \"Line $i\"; sleep 0.5; done'"
    )
    print(f"Exit code: {code}\n")

    # Example 4: Command with error output
    print("\n4. Command with error output:")
    print("-" * 50)
    code = execute_command_realtime("ls /nonexistent_directory_12345")
    print(f"Exit code: {code}\n")

    # Example 5: Combined output (stdout and stderr together)
    print("\n5. Combined output capture:")
    print("-" * 50)
    code, output = execute_command_realtime_combined("echo 'test output'")
    print(f"Exit code: {code}")
    print(f"Captured output length: {len(output)} bytes\n")

    # Example 6: Threaded execution
    print("\n6. Threaded execution (stdout and stderr separate):")
    print("-" * 50)
    code, stdout, stderr = execute_command_realtime_threaded("echo 'stdout message'")
    print(f"Exit code: {code}\n")

    # Example 7: With progress display
    print("\n7. Command with progress display:")
    print("-" * 50)
    code = execute_command_with_progress("pwd")
    print()

    # Example 8: Custom stdout callback
    print("\n8. Custom callback for output processing:")
    print("-" * 50)

    def custom_callback(line):
        print(f">>> {line.upper()}", end="")

    code, _, _ = execute_command_realtime_threaded(
        "echo 'this will be uppercase'", stdout_callback=custom_callback
    )
    print(f"Exit code: {code}\n")

    # Example 9: Stream with line callback
    print("\n9. Stream with line-by-line callback:")
    print("-" * 50)

    def line_processor(line, is_stderr):
        prefix = "[ERR]" if is_stderr else "[OUT]"
        print(f"{prefix} {line}", end="")

    code = stream_command_output("echo 'streamed output'", line_callback=line_processor)
    print(f"Exit code: {code}\n")

    # Example 10: Long-running command with real-time output
    print("\n10. Long-running command (ping 3 times):")
    print("-" * 50)
    code = execute_command_realtime("ping -c 3 127.0.0.1")
    print(f"Exit code: {code}\n")

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
