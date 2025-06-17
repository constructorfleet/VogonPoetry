"""Configuration loading module for Vogon Poetry."""

import yaml
from vogonpoetry.config import Configuration
from vogonpoetry.logging import logger

_logger  = logger(__name__)

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
    _logger.info("Raw Config", raw=raw, schema=Configuration.__pydantic_core_schema__)
    Configuration.model_rebuild()
    _logger.info("Rebuilt Config", schema=Configuration.__pydantic_core_schema__)   
    cfg = Configuration(**raw)
    _logger.info("Config", config=cfg)
    return cfg
