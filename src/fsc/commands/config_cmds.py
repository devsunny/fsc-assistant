

import os
import click
from fsc.config import ConfigManager

@click.group()
def config():
    """Manage FSC configuration."""
    pass


@config.command()
@click.argument(
    "key",
    required=True,
    nargs=1,
)
@click.argument(
    "value",
    required=True,
    nargs=1,
)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    help="Set the configuration globally.",
    default=False,
)
def set(key, value, is_global):
    """Set a configuration value.

    Arguments:
        key: Dot-separated key path to get (e.g., "database.password").
        value: The value to set.
    Options:
        --global / -g: Save the configuration globally.
    """
    manager = ConfigManager(
        ConfigManager.get_global_config_path() if is_global else None
    )
    manager.set(key, value, is_global=is_global)
    manager.save_config(is_global=is_global)


@config.command()
@click.argument(
    "key",
    required=True,
    nargs=1,
)
def get(key):
    """Get a configuration value.

    Arguments:
        key: Dot-separated key path to get (e.g., "database.password").
    """
    manager = ConfigManager()
    value = manager.get(key)
    if value is not None:
        print(f"{key} = {value}")
    else:
        print(f"Key '{key}' not found in configuration.")


@config.command()
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    help="Save the configuration globally.",
    default=False,
)
@click.argument(
    "key",
    required=True,
    nargs=1,
)
def delete(key, is_global):
    """Delete a configuration entry.

    Arguments:
        key: Dot-separated key path to get (e.g., "database.password").
    """
    manager = ConfigManager(
        ConfigManager.get_global_config_path() if is_global else None
    )
    if key:
        keys = key.split(".")
        current = manager.config
        for i, k in enumerate(keys):
            if k in current:
                if i == len(keys) - 1:
                    del current[k]
                    print(f"Deleted key '{key}'.")
                else:
                    current = current[k]
            else:
                print(f"Key '{key}' not found in configuration.")
                return
        manager.save_config(is_global=is_global)


@config.command()
def init():
    """Initialize a new configuration file in the current directory."""
    dir = os.path.abspath(os.getcwd())
    file_name = ConfigManager.CONFIG_FILE
    file_path = os.path.join(dir, file_name)
    if os.path.exists(file_path):
        print("Configuration file already exists. Use 'set' to modify values.")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            toml.dump({}, f)
        print("Initialized new configuration file in the current directory.")


@config.command()
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    help="Save the configuration globally.",
    default=False,
)
def show(is_global):
    """Display the current configuration."""
    manager = ConfigManager()
    if manager._is_loaded:
        if is_global:
            print(f"Global Configuration: {manager.global_config_file}")
            print(toml.dumps(manager.global_config))
        else:
            print(f"Local Configuration: {manager.load_config_file}")
            print(manager)
    else:
        print("No configuration loaded.")