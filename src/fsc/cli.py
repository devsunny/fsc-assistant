import click

from .commands.shell_cmds import assistant_shell
from .commands.config_cmds import config
from .config import configman


@click.group()
def cli():
    """An AI coding assistant."""
    pass


cli.add_command(assistant_shell, "shell")
cli.add_command(config, "config")


if __name__ == "__main__": 
    cli()