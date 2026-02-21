"""Configuration directory management using platformdirs"""
from pathlib import Path
import platformdirs

# Application info
APP_NAME = "termcap"
APP_AUTHOR = "rexwzh"

def get_config_dir() -> Path:
    """Get configuration directory path"""
    path = Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_data_dir() -> Path:
    """Get data directory path"""
    path = Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_templates_dir() -> Path:
    """Get templates directory path"""
    path = get_config_dir() / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_config_file() -> Path:
    """Get config file path"""
    return get_config_dir() / "config.toml"
