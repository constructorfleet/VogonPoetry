import pytest
import tempfile
import yaml
import os
from vogonpoetry.loader import load_config

SAMPLE_CONFIG = {
    "name": "Test Config",
    "description": "A test configuration",
    "version": "1.0",
    "mcp_servers": [],
    "embedders": [],
    "pipeline": {
        "id": "test_pipeline",
        "description": "Test pipeline",
        "steps": []
    }
}

def test_load_config_success(monkeypatch):
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        yaml.dump(SAMPLE_CONFIG, tf)
        tf.flush()
        config_path = tf.name

    config = load_config(config_path)
    assert config.pipeline.id == "test_pipeline"
    assert config.pipeline.description == "Test pipeline"
    os.remove(config_path)