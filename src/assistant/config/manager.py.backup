# assistant_config.py
import json
import os
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import tomlkit


class AssistantConfig:
    """
    Configuration manager for Kara Code projects using TOML file format.

    This class provides an API for managing configuration files with support for
    sections (tables), key-value pairs, and hierarchical file discovery from
    current directory to project root and user home directory.

    Attributes:
        config_filename (str): Name of the configuration file
        config_data (Dict[str, Any]): Loaded configuration data
        config_file_path (Optional[Path]): Path to the active configuration file
    """

    CONFIG_FILENAME = ".fsc-assistant.env.toml"
    HOME_CONFIG_DIR = Path.home() / ".fsc-assistant"
    VALID_PROJECT_TYPES = [
        "flask",
        "fastapi",
        "mcp",
        "react",
        "vue3",
        "python",
        "rust",
        "golang",
    ]

    def __init__(self, global_only=False):
        """
        Initialize the AssistantConfig instance.

        Searches for configuration file from current directory up to project root,
        then in user home directory. Loads configuration if found, otherwise
        initializes with default structure.
        """
        self.global_only = global_only
        self.config_data: Dict[str, Any] = {}
        self.config_file_path: Optional[Path] = None
        self.global_config_path: Path = None
        self._load_config()

    def _load_config(self) -> None:
        """
        Load configuration from file system.

        Searches for .fsc-assistant.env.toml from current directory to root,
        then in user home directory. Merges configurations with closest
        file taking precedence.
        """
        self.config_file_path, self.global_config_path = self._find_config_files()

        self._initialize_default_config()

        if self.global_config_path and self.global_config_path.exists():
            with open(self.global_config_path, "rb") as f:
                file_config = tomllib.load(f)
                self._merge_config(file_config)

        if (
            self.global_only is False
            and self.config_file_path
            and self.config_file_path.exists()
        ):
            with open(self.config_file_path, "rb") as f:
                file_config = tomllib.load(f)
                self._merge_config(file_config)

    def _find_config_files(self) -> List[Path]:
        """
        Find all configuration files from current directory to root and home.

        Returns:
            List[Path]: List of configuration file paths, ordered from closest to furthest
        """
        config_file = None

        if self.global_only is False:
            # Search from current directory to root
            current_path = Path.cwd()
            while current_path != current_path.parent:
                config_file = current_path / self.CONFIG_FILENAME
                if config_file.exists():
                    break
                current_path = current_path.parent

        # Check user home directory
        home_config = self.HOME_CONFIG_DIR / self.CONFIG_FILENAME
        os.makedirs(self.HOME_CONFIG_DIR, exist_ok=True)
        return config_file, home_config

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge new configuration into existing configuration.

        Args:
            new_config (Dict[str, Any]): Configuration to merge
        """
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self.config_data:
                if isinstance(self.config_data[key], dict):
                    self.config_data[key].update(value)
                else:
                    self.config_data[key] = value
            else:
                self.config_data[key] = value

    def _initialize_default_config(self) -> None:
        """Initialize configuration with default structure."""
        self.config_data = {
            "project_name": "",
            "project_directory": "",
            "project_type": "python",
            "database": {"url": ""},
            "llm": {
                "base_url": "",
                "api_key": "",
                "provider": "litellm",
                "models": [],
                "tool_selection_model": "gpt-4o-mini",
                "max_selected_tools": 10,
                "tool_selection_cache_ttl": 300,
                "enable_tool_selection": True,
            },
            "jira": {
                "base_url": "",
                "username": "",
                "api_token": "",
                "default_project": "",
            },
            "github": {"token": "", "default_owner": "", "default_repo": ""},
            "mcp": {
                "registry": str(self.HOME_CONFIG_DIR / "mcp.json"),
                "enabled": True,
            },
        }

    def reload(self) -> None:
        """
        Reload configuration from file system.

        This method re-reads the configuration files from disk and updates
        the in-memory configuration data. Useful when configuration files
        have been modified externally or when you want to discard unsaved
        changes and revert to the file state.

        Example:
            >>> config = AssistantConfig()
            >>> config.set_project_name("MyProject")
            >>> # Discard unsaved changes
            >>> config.reload()
        """
        self._load_config()

    def add_section(self, section_name: str) -> None:
        """
        Add a new section (table) to the configuration.

        Args:
            section_name (str): Name of the section to add

        Raises:
            ValueError: If section already exists
        """
        if section_name in self.config_data:
            raise ValueError(f"Section '{section_name}' already exists")
        self.config_data[section_name] = {}

    def remove_section(self, section_name: str) -> None:
        """
        Remove a section from the configuration.

        Args:
            section_name (str): Name of the section to remove

        Raises:
            KeyError: If section does not exist
        """
        if section_name not in self.config_data:
            raise KeyError(f"Section '{section_name}' does not exist")
        del self.config_data[section_name]

    def _normalize_value(self, value: str) -> Any:
        if not isinstance(value, str):
            return value

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def add_value(self, section: str, key: str, value: Any) -> None:
        """
        Add a new key-value pair to a section.

        Args:
            section (str): Section name
            key (str): Key name
            value (Any): Value to add

        Raises:
            KeyError: If section does not exist
            ValueError: If key already exists in section
        """
        if section not in self.config_data:
            self.config_data[section] = {}

        if (
            isinstance(self.config_data[section], dict)
            and key in self.config_data[section]
        ):
            raise ValueError(f"Key '{key}' already exists in section '{section}'")

        if section in self.config_data and not isinstance(
            self.config_data[section], dict
        ):
            raise ValueError(f"Section '{section}' is not a table")

        self.config_data[section][key] = self._normalize_value(value)

    def update_value(self, section: str, key: str, value: Any) -> None:
        """
        Update an existing key-value pair in a section.

        Args:
            section (str): Section name
            key (str): Key name
            value (Any): New value

        Raises:
            KeyError: If section or key does not exist
        """
        if section not in self.config_data:
            raise KeyError(f"Section '{section}' does not exist")

        if section in self.config_data and isinstance(self.config_data[section], dict):
            self.config_data[section][key] = self._normalize_value(value)
        elif section in self.config_data:
            self.config_data[section] = self._normalize_value(value)
        else:
            raise KeyError(f"Cannot update value in section '{section}'")

    def remove_value(self, section: str, key: str) -> None:
        """
        Remove a key-value pair from a section.

        Args:
            section (str): Section name
            key (str): Key name to remove

        Raises:
            KeyError: If section or key does not exist
        """
        if section not in self.config_data:
            raise KeyError(f"Section '{section}' does not exist")
        if not isinstance(self.config_data[section], dict):
            raise ValueError(f"Section '{section}' is not a table")
        if key not in self.config_data[section]:
            raise KeyError(f"Key '{key}' does not exist in section '{section}'")

        del self.config_data[section][key]

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific section.

        Args:
            section_name (str): Name of the section

        Returns:
            Dict[str, Any]: Section configuration as dictionary

        Raises:
            KeyError: If section does not exist
        """
        if section_name not in self.config_data:
            raise KeyError(f"Section '{section_name}' does not exist")

        section_data = self.config_data[section_name]
        if isinstance(section_data, dict):
            return section_data.copy()
        else:
            return {section_name: section_data}

    def get_option(self, section_name: str, key_name: str, default=None) -> Any:
        """
        Get a specific option value from a section.

        Args:
            section_name (str): Name of the section
            key_name (str): Name of the key

        Returns:
            Any: Value of the specified option

        Raises:
            KeyError: If section or key does not exist
        """

        if section_name in self.config_data:
            if isinstance(self.config_data[section_name], dict):
                if key_name not in self.config_data[section_name]:
                    return default
                return self.config_data[section_name][key_name]

        return default

    def get_int(self, section_name: str, key_name: str, default=None) -> int:
        val = self.get_option(section_name, key_name, default=default)
        if val is not None:
            return int(val)
        return 0

    def get_float(self, section_name: str, key_name: str, default=None) -> int:
        val = self.get_option(section_name, key_name, default=default)
        if val is not None:
            return float(val)
        return 0.0

    def get_boolean(self, section_name: str, key_name: str, default=None) -> int:
        val = self.get_option(section_name, key_name, default=default)
        if val is not None and val.lower() in ["yes", "true", "y", "1"]:
            return True
        return False

    def save(self) -> None:
        """
        Save configuration to file.

        Args:
            global_flag (bool): If True, save to user home directory,
                              otherwise save to current directory
        """
        if self.global_only is True:
            save_path = self.HOME_CONFIG_DIR / self.CONFIG_FILENAME
            save_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            save_path = Path.cwd() / self.CONFIG_FILENAME

        try:
            # Create a TOML document object from the dictionary
            doc = tomlkit.document()

            # Iterate through the dictionary and add items to the TOML document
            for key, value in self.config_data.items():
                doc[key] = value

            # Open the file in write mode and dump the document
            with open(save_path, "w") as f:
                f.write(tomlkit.dumps(doc))
            print(f"Successfully saved data to {save_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        self.config_file_path = save_path

    def set_project_name(self, name: str) -> None:
        """
        Set the project name in global configuration.

        Args:
            name (str): Project name
        """
        self.config_data["project_name"] = name

    def set_project_directory(self, directory: str) -> None:
        """
        Set the project directory in global configuration.

        Args:
            directory (str): Project directory path
        """
        self.config_data["project_directory"] = directory

    def set_project_type(self, project_type: str) -> None:
        """
        Set the project type in global configuration.

        Args:
            project_type (str): Project type (must be one of valid types)

        Raises:
            ValueError: If project type is not valid
        """
        if project_type not in self.VALID_PROJECT_TYPES:
            raise ValueError(
                f"Invalid project type. Must be one of: {self.VALID_PROJECT_TYPES}"
            )
        self.config_data["project_type"] = project_type

    def get_project_name(self) -> str:
        """
        Get the project name from configuration.

        Returns:
            str: Project name or empty string if not set
        """
        return self.config_data.get("project_name", "")

    def get_project_directory(self) -> str:
        """
        Get the project directory from configuration.

        Returns:
            str: Project directory or empty string if not set
        """
        return self.config_data.get("project_directory", "")

    def get_project_type(self) -> str:
        """
        Get the project type from configuration.

        Returns:
            str: Project type or 'python' as default
        """
        return self.config_data.get("project_type", "python")


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Apply to global configuration.",
)
@click.argument("config_entry", nargs=-1, type=str)
def set_llm_config(config_entry: List[str], global_config: bool = False):
    """get or set Kara Code LLM configuration"""
    config = AssistantConfig(global_config)
    if len(config_entry) == 0:
        return
    elif len(config_entry) == 1:
        print(config.get_option("llm", config_entry[0]))
    elif len(config_entry) == 2:
        if config_entry[0].lower() in ["delete", "remove"]:
            config.remove_value("llm", config_entry[1])
        elif config.get_option("llm", config_entry[0]):
            config.update_value("llm", config_entry[0], config_entry[1])
        else:
            config.add_value("llm", config_entry[0], config_entry[1])
        config.save()


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Apply to global configuration.",
)
@click.argument("config_entry", nargs=-1, type=str)
def set_config(config_entry: List[str], global_config: bool = False):
    """set Kara Code configuration"""
    config = AssistantConfig(global_config)
    if len(config_entry) <= 1:
        click.echo(
            "must provide section, name , and  value  or name and value to set config"
        )
        return
    elif len(config_entry) == 2:
        cfgps = config_entry[0].split(".")
        if len(cfgps) > 1:
            if cfgps[0] in config.config_data:
                config.update_value(cfgps[0], ".".join(cfgps[1:]), config_entry[1])
            else:
                config.add_value(cfgps[0], ".".join(cfgps[1:]), config_entry[1])
        else:
            config.config_data[config_entry[0]] = config_entry[1]
        config.save()
    elif len(config_entry) == 3:
        if config.get_option(config_entry[0], config_entry[1]):
            config.update_value(config_entry[0], config_entry[1], config_entry[2])
        else:
            config.add_value(config_entry[0], config_entry[1], config_entry[2])
        config.save()
    else:
        if config.get_option(config_entry[0], config_entry[1]):
            config.update_value(config_entry[0], config_entry[1], config_entry[2:])
        else:
            config.add_value(config_entry[0], config_entry[1], config_entry[2:])
        config.save()


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Apply to global configuration.",
)
@click.argument("config_entry", nargs=-1, type=str)
def get_config(config_entry: List[str], global_config: bool = False):
    """get Kara Code configuration"""
    config = AssistantConfig(global_config)
    if len(config_entry) == 1:
        if "." in config_entry[0]:
            cfgps = config_entry[0].split(".")
            print(config.get_option(cfgps[0], cfgps[1]))
        else:
            print(config.config_data[config_entry[0]])
        return
    elif len(config_entry) >= 2:
        print(config.get_option(config_entry[0], config_entry[1]))


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Apply to global configuration.",
)
@click.argument("config_entry", nargs=-1, type=str)
def remove_config(config_entry: List[str], global_config: bool = False):
    """remove Kara Code configuration"""
    config = AssistantConfig(global_config)
    if len(config_entry) == 1:
        if "." in config_entry[0]:
            cfgps = config_entry[0].split(".")
            config.remove_value(cfgps[0], cfgps[1])
        else:
            del config.config_data[config_entry[0]]
        return
    elif len(config_entry) >= 2:
        config.remove_value(config_entry[0], config_entry[1])
    config.save()


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Show global configuration.",
)
@click.argument("section_names", nargs=-1, type=str)
def show_config(global_config: bool = False, section_names=None):
    """show Kara Code configuration"""
    config = AssistantConfig(global_config)
    print(f"Config file:{config.config_file_path}")
    if section_names:
        sub_cfg = {
            sec: config.config_data[sec]
            for sec in section_names
            if sec in config.config_data
        }
        toml_string = tomlkit.dumps(sub_cfg)
    else:
        toml_string = tomlkit.dumps(config.config_data)
    print(toml_string)


@click.command
@click.option(
    "--global-config",
    "-g",
    is_flag=True,
    default=False,
    help="Show global configuration.",
)
@click.argument("model_ids", nargs=-1, type=str)
def add_models(global_config: bool = False, model_ids=None):
    """add models to Kara Code configuration"""
    if model_ids:
        config = AssistantConfig(global_config)
        print(f"Config file:{config.config_file_path}")
        models = config.get_option("llm", "models")
        if models is None:
            config.add_value("llm", "models", model_ids)
        else:
            if not isinstance(models, list):
                models = [models]
            models.extend(model_ids)
            config.update_value("llm", "models", models)
        config.save()


@click.group
def config():
    """Kara Code configuration manipulation"""


config.add_command(set_llm_config, "llm")
config.add_command(set_config, "set")
config.add_command(get_config, "get")
config.add_command(remove_config, "remove")
config.add_command(show_config, "show")
config.add_command(add_models, "add-model")
