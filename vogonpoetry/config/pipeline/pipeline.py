""""Pipeline configuration for the Vogon Poetry project."""
from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from vogonpoetry.config.pipeline.steps.base import BaseStep


class PipelineConfig(BaseModel):
    """Base configuration for the pipeline."""
    name: Annotated[str, Field(description="Name of the pipeline.")]
    description: Annotated[Optional[str], Field(default=None, description="Description of the pipeline.")]
    steps: Annotated[BaseStep, Field(description="Steps in the pipeline.")]