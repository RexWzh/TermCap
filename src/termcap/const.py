import platformdirs
from pathlib import Path

# dirs
TERMCAP_CACHE_DIR = Path(platformdirs.user_cache_dir('termcap'))
TERMCAP_CONFIG_DIR = Path(platformdirs.user_config_dir('termcap'))

