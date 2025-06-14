"""Prompt merging step configuration for the pipeline."""

from enum import Enum
from typing import Annotated, Dict, Literal, Optional, Union

from pydantic import Field

from vogonpoetry.config.pipeline.steps.base import BaseStepConfig

MergeStrategy = Literal['concatenate'] | Literal['json'] | Literal['replace']

class MergePromptsStepConfig(BaseStepConfig):
    """Base configuration class for merging prompts in the pipeline."""
    type: Annotated[Literal['merge_prompts'], Field('merge_prompts', pattern=r'^merge_prompts$')]
    strategy: Annotated[MergeStrategy, Field(description="The strategy to use for merging prompts.", default='concatenate')]
