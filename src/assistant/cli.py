"""
KARA Code CLI - Main entry point with lazy loading for fast startup.

This module uses lazy imports to minimize startup time. Heavy dependencies
like docling, transformers, torch, and psycopg2 are only loaded when their
respective commands are actually invoked.
"""

import sys
import click

from .__version__ import __version__


class LazyGroup(click.Group):
    """
    A click Group that imports commands lazily.

    This significantly improves CLI startup time by only importing
    command modules when they are actually invoked, rather than
    importing everything at CLI initialization.
    """

    def __init__(self, *args, lazy_subcommands=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Map of command name -> (module_path, function_name)
        self.lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx):
        """List all available commands."""
        return sorted(self.lazy_subcommands.keys())

    def get_command(self, ctx, cmd_name):
        """Get a command, importing it lazily if needed."""
        if cmd_name in self.lazy_subcommands:
            module_path, func_name = self.lazy_subcommands[cmd_name]

            # Import the module
            import importlib

            module = importlib.import_module(module_path)

            # Get the command function
            return getattr(module, func_name)

        return None


def should_show_banner():
    """
    Determine if we should show the banner.

    Skip banner for:
    - --help flag
    - --version flag
    - Non-interactive commands
    """
    args = sys.argv[1:]

    # Skip for help and version
    if "--help" in args or "-h" in args:
        return False
    if "--version" in args:
        return False

    # Skip if no command (just 'fsc-assistant')
    if not args:
        return False

    return True


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        # Fast commands (no heavy dependencies)
        "config": ("assistant.config.manager", "config"),
        "llm": ("assistant.llm.commands", "llm"),
        "openspec": ("assistant.integrations.openspec", "openspec_group"),
        "shell": ("assistant.agents.shell", "code_shell"),
    },
)
@click.version_option(
    version=__version__,
    prog_name="fsc-assistant",
    message="%(prog)s, version %(version)s",
)
def cli():
    """KARA Code - AI-powered development assistant.

    An intelligent development tool that helps with code generation, review,
    refactoring, testing, and more using large language models (LLMs) and
    Model Context Protocol (MCP).
    """
    # Only show banner for interactive commands
    if should_show_banner():
        from .welcome import render_assistant_banner

        render_assistant_banner()


def warn_llm_config():
    """
    Display a warning message to the user about configuring LLM settings.
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    # Create the warning message
    warning_text = Text()
    warning_text.append("⚠️  LLM Configuration Required\n\n", style="bold yellow")
    warning_text.append(
        "Please configure your LLM settings before proceeding:\n\n", style="white"
    )
    warning_text.append("  • ", style="yellow")
    warning_text.append("base_url: ", style="bold cyan")
    warning_text.append("https://litellm-dev.kkr.cloud\n", style="green")
    warning_text.append("  • ", style="yellow")
    warning_text.append("api_key: ", style="bold cyan")
    warning_text.append("<your-api-key>\n\n", style="green")
    warning_text.append(
        "\nfsc-assistant config set 'llm.base_url' 'https://litellm-dev.kkr.cloud' ",
        style="green",
    )
    warning_text.append(
        "\nfsc-assistant config set 'llm.api_key' '<your_api_key>' ", style="green"
    )
    warning_text.append("  • ", style="yellow")
    warning_text.append(
        "after you set base_url and api_key, you can the following command to list models ",
        style="green",
    )
    warning_text.append("\nfsc-assistant llm models", style="green")
    warning_text.append(
        '\nfsc-assistant config set \'llm.models\' "[\\"qwen3-coder-480b-a35b\\",\\"anthropic.claude-sonnet-4-5\\"] ',
        style="green",
    )
    warning_text.append(
        "\nfsc-assistant config set 'llm.max_completion_tokens' 32000", style="green"
    )
    warning_text.append(
        "Set these values in your environment or configuration file.",
        style="italic dim",
    )

    # Display the warning in a panel
    console.print(
        Panel(
            warning_text,
            border_style="yellow",
            padding=(1, 2),
            title="[bold red]Configuration Warning[/bold red]",
            title_align="left",
        )
    )


if __name__ == "__main__":
    from .config.manager import AssistantConfig

    cfg = AssistantConfig()
    if (
        not cfg.get_section("llm")
        or not cfg.get_option("llm", "base_url")
        or not cfg.get_option("llm", "api_key")
    ):
        warn_llm_config()

    cli()
