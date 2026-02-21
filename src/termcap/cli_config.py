"""CLI commands for configuration management"""
from termcap.config import get_config_manager, get_config_file, get_templates_dir

def show_config():
    """Display current configuration"""
    manager = get_config_manager()
    config = manager.load_config()
    
    print(f"Configuration file: {get_config_file()}")
    print(f"Templates directory: {get_templates_dir()}")
    
    for section, settings in config.items():
        print(f"\n[{section}]")
        for key, value in settings.items():
            print(f"  {key} = {value}")

def list_templates():
    """List all available templates"""
    manager = get_config_manager()
    templates = manager.get_available_templates()
    
    print("Available templates:")
    for name in sorted(templates.keys()):
        path = templates[name]
        if path is None:
            print(f"  {name} (builtin)")
        else:
            print(f"  {name} (custom: {path})")

def reset_config():
    """Reset configuration to defaults"""
    manager = get_config_manager()
    manager.reset_config()
    print("Configuration reset to defaults.")
