import os

from termcap.config import get_config_manager


def get_default_settings():
    manager = get_config_manager()
    config = manager.load_config()
    return {
        "template": config["general"]["default_template"],
        "geometry": config["general"]["default_geometry"],
        "min_duration": config["general"]["default_min_duration"],
        "max_duration": config["general"]["default_max_duration"],
        "loop_delay": config["general"]["default_loop_delay"],
        "command": os.environ.get("SHELL", "/bin/bash"),
    }
