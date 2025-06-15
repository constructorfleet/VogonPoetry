"""Vogon Poetry Configuration"""

from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from vogonpoetry.config.embedders import EmbedderConfig
from vogonpoetry.config.pipeline.pipeline import PipelineConfig


class Configuration(BaseModel):
    """Base configuration for the Vogon Poetry project."""
    name: Annotated[str, Field(description="Name of the configuration.")]
    description: Annotated[Optional[str], Field(default=None, description="Description of the configuration.")]
    version: Annotated[Optional[str], Field(default=None, description="Version of the configuration.")]
    pipeline: Annotated[PipelineConfig, Field(description="List of pipelines in the configuration.")]
    embedders: Annotated[list[EmbedderConfig], Field(description="List of embedders in the configuration.")]