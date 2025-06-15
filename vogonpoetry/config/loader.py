"""Configuration loading module for Vogon Poetry."""

import yaml
from vogonpoetry.config.config import Configuration
import logging

logger  = logging.getLogger(__name__)

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
    logger.info(f"load_config|raw|{raw}")
    cfg = Configuration.model_validate(raw)
    logger.info(f"load_config|cfg|{cfg}")
    return cfg
