from pathlib import Path

from common.utils import copy_file

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent

# Dirs
LOG_DIR = BASE_DIR / "log"

# Config
CONFIG_DIR = BASE_DIR / "config"
DEFAULT_CONFIG_DIR = CONFIG_DIR / ".default"

# In/Out
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Creating dirs and files
for dirpath in (INPUT_DIR, OUTPUT_DIR, LOG_DIR):
    dirpath.mkdir(exist_ok=True)

# Creating copies
DEFAULT_CONFIG_TOML = DEFAULT_CONFIG_DIR / "config.toml"
CONFIG_TOML = CONFIG_DIR / "config.toml"
copy_file(DEFAULT_CONFIG_TOML, CONFIG_TOML)
