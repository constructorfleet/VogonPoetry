"""Prompt merging step configuration for the pipeline."""

from enum import Enum
from typing import Annotated, Dict, Literal, Optional

from pydantic import Field

MergeStrategy = Literal['concatenate'] | Literal['json'] | Literal['replace']

class MergePrompts:
    """Base configuration class for merging prompts in the pipeline."""
    type: Annotated[Literal['merge_prompts'], Field('merge_prompts', pattern=r'^merge_prompts$')]
    strategy: Annotated[MergeStrategy, Field(description="The strategy to use for merging prompts.", default='concatenate')]
