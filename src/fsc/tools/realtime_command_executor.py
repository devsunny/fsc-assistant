import os
import subprocess
import threading
import sys
import platform
from typing import Dict

def execute_system_command_realtime(command,  shell:bool = False, env: Dict[str, str]=None, stdout_prefix="", stderr_prefix="<ERROR>: ") -> tuple:
    """
    Executes a system command and prints its stdout and stderr in real-time.

    This function runs a command in a separate process and uses threads to
    continuously read and print the standard output and standard error streams,
    each with a specified prefix. It waits for the command to complete and
    returns the final exit code and the full captured output.

    Args:
        command (list): The command to execute as a list of strings
                        (e.g., ["ping", "google.com"]).
        shell (bool): Whether to execute the command through the shell.
        env (Dict[str, str], optional): Environment variables to set for the command.
        stdout_prefix (str): The string to prepend to each line of stdout.
        stderr_prefix (str): The string to prepend to each line of stderr.

    Returns:
        tuple: A tuple containing two elements:
               - The integer exit code of the command.
               - A string containing the complete, interleaved stdout and stderr.
    """
    # A list to hold all output lines for the final result
    output_lines = []
    # A lock to ensure that printing to the console and appending to the list
    # are thread-safe operations.
    lock = threading.Lock()

    def reader_thread(stream, prefix):
        """
        A target function for threads. It reads from a given stream (stdout/stderr),
        prefixes each line, prints it, and adds it to a shared list.
        """
        # Read lines from the stream until it is closed
        for line in iter(stream.readline, ''):
            with lock:
                # Print the output to the console in real-time
                sys.stdout.write(f"{prefix}{line}")
                sys.stdout.flush()
                # Add the original line to our list for the final result
                output_lines.append(line)
        stream.close()

    try:
        # Start the subprocess.
        # - `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` redirect the streams
        #   so we can read them.
        # - `text=True` decodes the byte streams into text using the default encoding.
        # - `bufsize=1` enables line-buffering for better real-time output.
        process = subprocess.Popen(
            command,
            shell=shell,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print(f"Error: Command not found: '{command[0]}'", file=sys.stderr)
        return -1, f"Command not found: {command[0]}"
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return -1, str(e)


    # Create two threads to read from stdout and stderr concurrently
    stdout_reader = threading.Thread(target=reader_thread, args=(process.stdout, stdout_prefix))
    stderr_reader = threading.Thread(target=reader_thread, args=(process.stderr, stderr_prefix))

    # Start the threads
    stdout_reader.start()
    stderr_reader.start()

    # Wait for the process to terminate and get its return code
    return_code = process.wait()

    # Wait for the reader threads to finish reading any remaining output
    stdout_reader.join()
    stderr_reader.join()

    # Join all the captured lines into a single string
    full_output = "".join(output_lines)

    return return_code, full_output

def execute_shell_command_realtime(command: str) -> tuple:
    """
    Executes a shell command in a platform-independent way and prints its output in real-time.

    This function determines the appropriate shell to use based on the operating system
    and then calls `execute_system_command_realtime` to execute the command.

    Args:
        command (str): The shell command to execute as a single string.

    Returns:
        tuple: A tuple containing two elements:
               - The integer exit code of the command.
               - A string containing the complete, interleaved stdout and stderr.
    """  
    return execute_system_command_realtime(command, 
                                           env=os.environ,
                                           shell=True, 
                                           stdout_prefix="", 
                                           stderr_prefix="[ERROR]: ")    