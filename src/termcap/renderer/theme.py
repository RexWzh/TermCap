"""Theme and template management for renderer"""
from typing import Dict, Any, Optional
from termcap.config.manager import get_config_manager

def load_template(template_name: str) -> Optional[bytes]:
    """Load an SVG template by name"""
    manager = get_config_manager()
    return manager.get_template_content(template_name)
