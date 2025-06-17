"""Prompt merging step configuration for the pipeline."""

from enum import Enum
from typing import Annotated, Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, Field

from vogonpoetry.context import BaseContext
from vogonpoetry.logging import logger
from vogonpoetry.pipeline.steps.base import BaseStep

MergeStrategy = Literal['concatenate'] | Literal['json'] | Literal['replace']

class MergePromptsStepOptions(BaseModel):
    strategy: Annotated[MergeStrategy, Field(description="The strategy to use for merging prompts.", default='concatenate')]

class MergePromptsStep(BaseStep[MergePromptsStepOptions, Dict[str, Any]]):
    """Base configuration class for merging prompts in the pipeline."""
    type: Literal['merge_prompts'] = 'merge_prompts'
    strategy: Annotated[MergeStrategy, Field(description="The strategy to use for merging prompts.", default='concatenate')]

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"MergePromptsStep-{self.id}")
        return super().model_post_init(context)

    async def _process_step(self, context: BaseContext) -> Dict[str, Any]:
        return {}
        # values = [context.get(k) for k in self.input_keys]
        # if self.strategy == "concat":
        #     return "\n".join([v for v in values if v])
        # elif self.strategy == "json":
        #     return {f"input_{i}": v for i, v in enumerate(values)}
        # else:
        #     raise ValueError(f"Unknown merge strategy: {self.strategy}")