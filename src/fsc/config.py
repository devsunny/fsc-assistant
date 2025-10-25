import logging
import tomlkit as toml
import os
import json
import copy
import click
from pathlib import Path

logger=logging.getLogger(__name__)


# --- TOMLConfigManager Class ---
class ConfigManager:
    """
    A class to manage reading and writing TOML configuration files with
    built-in encryption for sensitive fields like 'password' and 'api_key'.
    """

    CONFIG_FILE = ".config.toml"

    # Define sensitive keys that should be encrypted
    _SENSITIVE_KEYS = {"password", "api_key"}

    def __init__(self, cfg_file_path: str = None):
        self.cfg_file_path = cfg_file_path
        self.load_config_file = cfg_file_path
        self.global_config_file = ConfigManager.get_global_config_path()
        self.config = {}
        self.global_config = {}
        self._is_loaded = False  # Track if a config has been successfully loaded
        self.load_config()

    def _find_file_in_parent_tree(self):
        if self.cfg_file_path is not None:
            os.makedirs(os.path.dirname(self.cfg_file_path), exist_ok=True)
            self.load_config_file = os.path.abspath(self.cfg_file_path)
            return self.load_config_file

        dir = os.path.abspath(os.getcwd())
        root_dir = os.path.abspath(os.sep)
        file_name = ConfigManager.CONFIG_FILE
        while dir != root_dir:
            file_path = os.path.join(dir, file_name)
            if os.path.exists(file_path):
                self.load_config_file = file_path
                return file_path
            dir = os.path.dirname(dir)

        return self.get_global_config_path()

    @staticmethod
    def get_global_config_path():
        home_directory = Path.home()
        global_fsc_cfg_dir = home_directory / ".fsc"
        os.makedirs(global_fsc_cfg_dir, exist_ok=True)
        return global_fsc_cfg_dir / ConfigManager.CONFIG_FILE

    def _load_config(self, file_path):
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_config = toml.load(f)                
                return raw_config
        except toml.TomlDecodeError as e:
            raise ValueError(f"Error decoding TOML file '{file_path}': {e}")
        except Exception as e:
            raise RuntimeError(
                f"An unexpected error occurred while loading config from '{file_path}': {e}"
            )

    def load_config(self):
        file_path = self._find_file_in_parent_tree()
        self.config = self._load_config(file_path)
        self.global_config = self._load_config(
            ConfigManager.get_global_config_path()
        )
        self._is_loaded = True

    def save_config(self, is_global=False):
        if is_global:
            file_path = self.get_global_config_path()
        else:
            file_path = self._find_file_in_parent_tree()

        # Create a deep copy to encrypt for saving without altering the active decrypted config
        cfg = self.config if not is_global else self.global_config
        config_to_save = copy.deepcopy(cfg)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                toml.dump(config_to_save, f)
            print(f"Configuration saved and encrypted to '{file_path}'.")
        except Exception as e:
            raise RuntimeError(f"Error saving TOML file '{file_path}': {e}")

    def _get_value(self, key_path, config, default=None):
        keys = key_path.split(".")
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default           
        return current
    
    def get_int(self, key_path: str, default=None):
        """
        Retrieves an integer value from the configuration using a dot-separated path.

        Args:
            key_path (str): The dot-separated path to the desired key (e.g., "database.port").
            default: The default value to return if the key path is not found.      
        Returns:
            The integer value at the specified key path, or the default value if not found.
        """
        value = self.get(key_path, default=default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default  
        
    def get_bool(self, key_path: str, default=None):
        """
        Retrieves a boolean value from the configuration using a dot-separated path.

        Args:
            key_path (str): The dot-separated path to the desired key (e.g., "feature.enabled").
            default: The default value to return if the key path is not found.
        Returns:
            The boolean value at the specified key path, or the default value if not found.
        """
        value = self.get(key_path, default=default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"true", "1", "yes", "on"}
        return bool(value) if value is not None else default        
    
    def get_float(self, key_path: str, default=None):
        """
        Retrieves a float value from the configuration using a dot-separated path.

        Args:
            key_path (str): The dot-separated path to the desired key (e.g., "settings.threshold").
            default: The default value to return if the key path is not found.  
        Returns:
            The float value at the specified key path, or the default value if not found.
        """
        value = self.get(key_path, default=default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get(self, key_path: str, default=None):
        """
        Retrieves a value from the configuration using a dot-separated path.

        Args:
            key_path (str): The dot-separated path to the desired key (e.g., "database.host").
            default: The default value to return if the key path is not found.

        Returns:
            The value at the specified key path, or the default value if not found.
        """
        # First check in local config, then in global config
        value = self._get_value(key_path, self.config, default=None)
        if value is not None:
            return value

        # print(json.dumps(self.global_config, indent=2))  # --- IGNORE ---
        return self._get_value(key_path, self.global_config, default=default)

    def set(self, key_path: str, value, is_global=False):
        """
        Sets a value in the configuration using a dot-separated path.
        This will update the internal decrypted configuration.

        Args:
            key_path (str): The dot-separated path to the key to set.
            value: The value to set.
        """
        keys = key_path.split(".")
        try:
            value = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            pass
        current = self.config if not is_global else self.global_config
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                # Last key, set the value
                current[key] = value
            else:
                # Not the last key, traverse or create nested dictionary
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
        print(f"Set '{key_path}' to '{value}'.")
        self._is_loaded = True

    def __str__(self):
        """Returns a string representation of the currently loaded (decrypted) config."""
        return toml.dumps(self.config)


configman = ConfigManager()

