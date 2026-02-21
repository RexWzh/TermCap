import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from termcap.config.manager import ConfigManager, DEFAULT_CONFIG

@pytest.fixture
def mock_config_paths(tmp_path):
    # Use tmp_path for config file and templates dir
    config_file = tmp_path / "config.toml"
    templates_dir = tmp_path / "templates"
    
    with patch('termcap.config.manager.get_config_file') as mock_file, \
         patch('termcap.config.manager.get_templates_dir') as mock_dir:
        mock_file.return_value = config_file
        mock_dir.return_value = templates_dir
        yield mock_file, mock_dir

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset ConfigManager singleton before each test"""
    # Reset singleton state if it exists (though implementation doesn't expose reset)
    # Since ConfigManager is not a strict singleton (it's just a global variable),
    # we can just re-instantiate or ensure tests don't rely on global state.
    # However, the implementation has:
    # _config_manager = None
    # def get_config_manager(): ...
    
    # We should reset _config_manager in the module
    import termcap.config.manager
    termcap.config.manager._config_manager = None

def test_load_default_config(mock_config_paths):
    mock_file, _ = mock_config_paths
    # File doesn't exist initially
    
    manager = ConfigManager()
    config = manager.load_config()
    
    assert config == DEFAULT_CONFIG
    assert mock_file.return_value.exists()

def test_load_existing_config(mock_config_paths):
    mock_file, _ = mock_config_paths
    
    # Create existing config
    mock_content = """
    [general]
    default_template = "custom"
    """
    mock_file.return_value.parent.mkdir(parents=True, exist_ok=True)
    mock_file.return_value.write_text(mock_content, encoding='utf-8')
    
    manager = ConfigManager()
    config = manager.load_config()
    
    assert config['general']['default_template'] == "custom"
    # Ensure defaults are merged
    assert 'default_geometry' in config['general']
    assert config['general']['default_geometry'] == DEFAULT_CONFIG['general']['default_geometry']

def test_get_setting(mock_config_paths):
    manager = ConfigManager()
    value = manager.get_setting('general', 'default_template')
    assert value == 'gjm8'
    
    default_val = manager.get_setting('nonexistent', 'key', 'default')
    assert default_val == 'default'

def test_set_setting(mock_config_paths):
    manager = ConfigManager()
    manager.set_setting('general', 'default_template', 'new_template')
    
    # Reload to verify persistence
    manager = ConfigManager() # New instance to force reload
    manager._config = None
    config = manager.load_config()
    assert config['general']['default_template'] == 'new_template'

def test_available_templates(mock_config_paths):
    mock_file, mock_dir = mock_config_paths
    mock_dir.return_value.mkdir(parents=True, exist_ok=True)
    
    # Create custom template file
    (mock_dir.return_value / "my_custom.svg").touch()
    
    manager = ConfigManager()
    templates = manager.get_available_templates()
    
    assert "gjm8" in templates
    assert "my_custom" in templates
    assert templates["gjm8"] is None  # Builtin
    assert templates["my_custom"] == mock_dir.return_value / "my_custom.svg"  # Custom
