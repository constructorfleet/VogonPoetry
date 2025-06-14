""""Pipeline configuration for the Vogon Poetry project."""
from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from vogonpoetry.config.pipeline.steps.base import BaseStep


class PipelineConfig(BaseModel):
    """Base configuration for the pipeline."""
    id: Annotated[str, Field(description="Identifier of the pipeline.")]
    description: Annotated[Optional[str], Field(default=None, description="Description of the pipeline.")]
    steps: Annotated[list[BaseStep], Field(description="Steps in the pipeline.")]