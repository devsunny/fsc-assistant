"""
OpenSpec Integration Command

This module provides CLI commands for integrating OpenSpec into Kara Code projects.
It handles automatic installation of OpenSpec if not present and provides a seamless
initialization experience with support for multiple subcommands.

Commands:
    openspec init: Initialize OpenSpec in the current project
    openspec list: List available OpenSpec tools
    openspec run: Run arbitrary OpenSpec commands interactively
"""

import shutil
import subprocess
import sys
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from assistant.utils.cli.executor import (
    execute_command_interactive,
    execute_command_realtime,
)

# Initialize Rich console for formatted output
console = Console()

# Default tool for OpenSpec initialization
DEFAULT_TOOL = "github-copilot"


def check_npm_installed() -> bool:
    """
    Check if npm is installed on the system.

    Returns:
        bool: True if npm is available, False otherwise

    Examples:
        >>> if check_npm_installed():
        ...     print("npm is available")
    """
    return shutil.which("npm") is not None


def check_openspec_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if OpenSpec is installed and get its version.

    Returns:
        Tuple[bool, Optional[str]]: (is_installed, version)
            - is_installed: True if openspec command is available
            - version: Version string if available, None otherwise

    Examples:
        >>> is_installed, version = check_openspec_installed()
        >>> if is_installed:
        ...     print(f"OpenSpec {version} is installed")
    """
    # Check if openspec command exists
    openspec_path = shutil.which("openspec")

    if not openspec_path:
        return False, None

    # Try to get version
    try:
        result = subprocess.run(
            ["openspec", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return True, None
    except Exception:
        # If version check fails, still return True since command exists
        return True, None


def install_openspec() -> int:
    """
    Install OpenSpec globally via npm.

    Returns:
        int: Exit code (0 = success, non-zero = failure)

    Examples:
        >>> exit_code = install_openspec()
        >>> if exit_code == 0:
        ...     print("Installation successful")
    """
    console.print("[yellow]Installing OpenSpec via npm...[/yellow]")
    console.print("[dim]This may take a minute...[/dim]\n")

    command = "npm install -g @fission-ai/openspec@latest"
    exit_code = execute_command_realtime(command)

    if exit_code == 0:
        console.print("\n[green]✓ OpenSpec installed successfully[/green]")

        # Verify installation and get version
        is_installed, version = check_openspec_installed()
        if is_installed and version:
            console.print(f"[green]  Version: {version}[/green]")
    else:
        console.print("\n[red]✗ OpenSpec installation failed[/red]")
        display_installation_error()

    return exit_code


def run_openspec_command(
    subcommand: str, args: Optional[list] = None, interactive: bool = False
) -> int:
    """
    Run an openspec command with optional arguments.

    Args:
        subcommand: The openspec subcommand (e.g., "init", "list")
        args: Additional arguments to pass to the command
        interactive: If True, run in interactive mode (allows user input)

    Returns:
        int: Exit code from openspec command

    Examples:
        >>> # Run openspec init with tools
        >>> exit_code = run_openspec_command("init", ["--tools", "claude,cursor"])

        >>> # Run openspec list interactively
        >>> exit_code = run_openspec_command("list", interactive=True)
    """
    # Build command
    command = f"openspec {subcommand}"
    if args:
        command += " " + " ".join(args)

    console.print(f"\n[cyan]Running: {command}[/cyan]")

    # Execute with appropriate mode
    if interactive:
        exit_code = execute_command_interactive(command)
    else:
        exit_code = execute_command_realtime(command)

    if exit_code == 0:
        console.print(f"\n[green]✓ openspec {subcommand} completed successfully[/green]")
    else:
        console.print(
            f"\n[red]✗ openspec {subcommand} failed (exit code: {exit_code})[/red]"
        )
        console.print("[yellow]Check the error messages above for details.[/yellow]")
        console.print("[dim]For help, visit: https://openspec.dev[/dim]")

    return exit_code


def ensure_openspec_installed() -> bool:
    """
    Ensure OpenSpec is installed, installing it if necessary.

    Returns:
        bool: True if OpenSpec is available, False if installation failed

    Examples:
        >>> if ensure_openspec_installed():
        ...     print("Ready to use OpenSpec")
    """
    console.print("[dim]Checking for npm...[/dim]")
    if not check_npm_installed():
        display_npm_not_found_error()
        return False

    console.print("[green]✓ npm is installed[/green]\n")

    console.print("[dim]Checking for OpenSpec...[/dim]")
    is_installed, version = check_openspec_installed()

    if is_installed:
        if version:
            console.print(
                f"[green]✓ OpenSpec is already installed (version {version})[/green]"
            )
        else:
            console.print("[green]✓ OpenSpec is already installed[/green]")
        return True
    else:
        console.print("[yellow]⚠ OpenSpec not found[/yellow]\n")
        exit_code = install_openspec()

        if exit_code != 0:
            console.print(
                "\n[red]Failed to install OpenSpec. Please install manually.[/red]"
            )
            return False

        return True


def display_npm_not_found_error() -> None:
    """Display error message when npm is not installed."""
    error_text = Text()
    error_text.append("✗ Error: npm is not installed\n\n", style="bold red")
    error_text.append("To install npm:\n", style="white")
    error_text.append("  • ", style="yellow")
    error_text.append("macOS: ", style="bold cyan")
    error_text.append("brew install node\n", style="green")
    error_text.append("  • ", style="yellow")
    error_text.append("Ubuntu/Debian: ", style="bold cyan")
    error_text.append("sudo apt install nodejs npm\n", style="green")
    error_text.append("  • ", style="yellow")
    error_text.append("Windows: ", style="bold cyan")
    error_text.append("Download from https://nodejs.org/\n\n", style="green")
    error_text.append(
        "After installing npm, run this command again.", style="italic dim"
    )

    console.print(
        Panel(
            error_text,
            border_style="red",
            padding=(1, 2),
            title="[bold red]npm Required[/bold red]",
            title_align="left",
        )
    )


def display_installation_error() -> None:
    """Display error message when OpenSpec installation fails."""
    console.print("\n[yellow]Possible causes:[/yellow]")
    console.print("  • Network connection issues")
    console.print(
        "  • Permission denied (try: [cyan]sudo npm install -g @fission-ai/openspec@latest[/cyan])"
    )
    console.print("  • npm registry unavailable")
    console.print("\n[yellow]Try installing manually:[/yellow]")
    console.print("  [cyan]npm install -g @fission-ai/openspec@latest[/cyan]")
    console.print("\n[dim]For more help, visit: https://openspec.dev[/dim]")


# ============================================================================
# CLI Commands
# ============================================================================


@click.group(name="openspec")
def openspec_group():
    """
    OpenSpec integration commands.

    Manage OpenSpec initialization, configuration, and usage within your project.
    OpenSpec provides AI-powered development tools and specifications.
    """
    console.print("\n[bold cyan]OpenSpec Integration[/bold cyan]\n")


@openspec_group.command(name="init")
@click.option(
    "--tools",
    type=str,
    default=None,
    help='Configure AI tools non-interactively. Use "all", "none", or comma-separated list: '
    "claude, cursor, factory, opencode, kilocode, windsurf, codex, github-copilot, amazon-q. "
    "Default: github-copilot",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=False,
    help="Run in interactive mode (allows OpenSpec to prompt for input)",
)
def init_command(tools: Optional[str], interactive: bool) -> None:
    """
    Initialize OpenSpec in your project.

    If OpenSpec is not installed, it will be automatically installed via npm.
    By default, initializes with github-copilot tool unless --tools is specified.

    Examples:

        # Initialize with default tool (github-copilot)
        kara-code openspec init

        # Initialize with specific tools
        kara-code openspec init --tools claude,cursor

        # Initialize with all tools
        kara-code openspec init --tools all

        # Interactive mode (OpenSpec will prompt for input)
        kara-code openspec init --interactive

    Note: Requires npm to be installed on your system.
    """
    if not ensure_openspec_installed():
        sys.exit(1)

    # Build arguments
    args = []
    if tools:
        args.extend(["--tools", tools])
    elif not interactive:
        # Use default tool only if not interactive and no tools specified
        console.print(f"[dim]Using default tool: {DEFAULT_TOOL}[/dim]")
        args.extend(["--tools", DEFAULT_TOOL])

    # Run openspec init
    exit_code = run_openspec_command("init", args, interactive=interactive)
    sys.exit(exit_code)


@openspec_group.command(name="list")
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=True,
    help="Run in interactive mode (default: True)",
)
def list_command(interactive: bool) -> None:
    """
    List available OpenSpec tools and configurations.

    This command shows all available AI tools that can be configured
    with OpenSpec, along with their current status.

    Examples:

        # List tools (interactive mode)
        kara-code openspec list

        # List tools (non-interactive)
        kara-code openspec list --no-interactive

    Note: Requires OpenSpec to be installed.
    """
    if not ensure_openspec_installed():
        sys.exit(1)

    exit_code = run_openspec_command("list", interactive=interactive)
    sys.exit(exit_code)


@openspec_group.command(name="run")
@click.argument("openspec_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=True,
    help="Run in interactive mode (allows user input, default: True)",
)
def run_command(openspec_args: tuple, interactive: bool) -> None:
    """
    Run arbitrary OpenSpec commands.

    This is a passthrough command that allows you to run any OpenSpec
    command with full support for user input and interaction.

    Examples:

        # Run openspec help
        kara-code openspec run --help

        # Run openspec with custom arguments
        kara-code openspec run validate --strict

        # Run openspec config
        kara-code openspec run config --show

        # Non-interactive mode
        kara-code openspec run status --no-interactive

    Note: All arguments after 'run' are passed directly to openspec.
    """
    if not ensure_openspec_installed():
        sys.exit(1)

    if not openspec_args:
        console.print("[yellow]No arguments provided to openspec[/yellow]")
        console.print("[dim]Usage: kara-code openspec run <openspec-command> [args][/dim]")
        console.print("[dim]Example: kara-code openspec run --help[/dim]")
        sys.exit(1)

    # Convert tuple to list for easier manipulation
    args = list(openspec_args)

    # The first arg is the subcommand, rest are arguments
    if args:
        subcommand = args[0]
        remaining_args = args[1:] if len(args) > 1 else None
        exit_code = run_openspec_command(subcommand, remaining_args, interactive=interactive)
    else:
        # Just run openspec with no subcommand (will show help)
        exit_code = run_openspec_command("", interactive=interactive)

    sys.exit(exit_code)


@openspec_group.command(name="version")
def version_command() -> None:
    """
    Show OpenSpec version.

    Displays the currently installed version of OpenSpec.

    Examples:

        kara-code openspec version
    """
    is_installed, version = check_openspec_installed()

    if not is_installed:
        console.print("[red]✗ OpenSpec is not installed[/red]")
        console.print("[dim]Run 'kara-code openspec init' to install[/dim]")
        sys.exit(1)

    if version:
        console.print(f"[green]OpenSpec version: {version}[/green]")
    else:
        console.print("[yellow]OpenSpec is installed but version could not be determined[/yellow]")
        # Try to run openspec --version directly
        run_openspec_command("--version", interactive=False)

    sys.exit(0)


@openspec_group.command(name="install")
def install_command() -> None:
    """
    Install or reinstall OpenSpec.

    Forces installation of OpenSpec even if it's already installed.
    Useful for upgrading to the latest version.

    Examples:

        # Install OpenSpec
        kara-code openspec install

        # Upgrade to latest version
        kara-code openspec install
    """
    console.print("[dim]Checking for npm...[/dim]")
    if not check_npm_installed():
        display_npm_not_found_error()
        sys.exit(1)

    console.print("[green]✓ npm is installed[/green]\n")

    exit_code = install_openspec()
    sys.exit(exit_code)


# Export the command group
__all__ = ["openspec_group"]
