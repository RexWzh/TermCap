import pkgutil

PKG_TEMPLATE_PATH = 'termcap/data/templates'

# Default configuration
DEFAULT_CONFIG = {
    "general": {
        "default_template": "gjm8",
        "default_geometry": "82x19",
        "default_min_duration": 17,
        "default_max_duration": 3000,
        "default_loop_delay": 1000,
    },
    "templates": {
        "custom_templates_enabled": True,
        "builtin_templates_enabled": True,
    },
    "output": {
        "default_output_dir": "~/termcap_recordings",
        "auto_timestamp": True,
    }
}

DEFAULT_TEMPLATES_NAMES = [
    'base16_default_dark.svg',
    'dracula.svg',
    'gjm8_play.svg',
    'gjm8_single_loop.svg',
    'gjm8.svg',
    'powershell.svg',
    'progress_bar.svg',
    'putty.svg',
    'solarized_dark.svg',
    'solarized_light.svg',
    'terminal_app.svg',
    'ubuntu.svg',
    'window_frame_js.svg',
    'window_frame_powershell.svg',
    'window_frame.svg',
    'xterm.svg',
]

def get_default_templates():
    """Return mapping between the name of a template and the SVG template itself"""
    templates = {}
    for template_name in DEFAULT_TEMPLATES_NAMES:
        # Note: We need to adjust the path relative to the package
        # Assuming termcap package structure
        # data is at src/termcap/data
        # This function might need adjustment depending on how data is packaged
        try:
            # Try loading from package data
            bstream = pkgutil.get_data('termcap', f'data/templates/{template_name}')
            if bstream:
                suffix = '.svg'
                name = template_name[:-len(suffix)] if template_name.endswith(suffix) else template_name
                templates[name] = bstream
        except Exception:
            pass

    return templates
