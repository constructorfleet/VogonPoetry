"""Configuration loading module for Vogon Poetry."""

from typing import Any, Dict, Optional
import yaml
from vogonpoetry.config.config import Configuration

def load_config(config_path: str) -> Configuration:
    """Load the configuration from a file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        Configuration: Loaded configuration object.
    """
    # Load the configuration from the specified path
    with open(config_path) as f:
        raw = yaml.safe_load(f)
    return Configuration.model_validate(raw)
