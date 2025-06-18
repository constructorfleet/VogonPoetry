"""Fork step configuration for the Vogon Poetry project."""
from __future__ import annotations
import asyncio
from typing import Annotated, Any, Literal, Sequence, TypeVar, Union

from pydantic import BaseModel, Field
from vogonpoetry.context import BaseContext
from vogonpoetry.pipeline import steps
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.pipeline.steps.types import PipelineStep as StepUnion

PipelineStep = Annotated[
    Union[StepUnion, 'ForkStep'],
    Field(
        description="Configuration for pipeline steps in the Vogon Poetry project.",
        discriminator="type"
    )
]


MergeStrategy = Literal['concatenate'] | Literal['replace'] | Literal['prefix']

class BaseForkStepOptions(BaseModel):
    """Options for the fork step in the pipeline."""
    steps: Annotated[Sequence['PipelineStep'], Field(description="List of steps to execute in parallel after the fork.")] # type: ignore

class ConcatenateStepOptions(BaseForkStepOptions):
    """Options for concatenating results from parallel steps."""
    merge_strategy: Literal['concatenate'] = 'concatenate'

class ReplaceStepOptions(BaseForkStepOptions):
    """Options for replacing results from parallel steps."""
    merge_strategy: Literal['replace'] = 'replace'

class PrefixStepOptions(BaseForkStepOptions):
    """Options for prefixing results from parallel steps."""
    merge_strategy: Literal['prefix'] = 'prefix'
    prefix: Annotated[str, Field(description="Prefix to add to keys from each step's result.")]


ForkStepOptions = Annotated[
    Union[
        ConcatenateStepOptions,
        ReplaceStepOptions,
        PrefixStepOptions,
    ],
    Field(discriminator="merge_strategy", description="Strategy to merge results from parallel steps.")
]

TStep = TypeVar("TStep", bound=BaseModel)


class ForkStep(BaseStep[ForkStepOptions, Any]):
    """Pipeline fork step configuration for the Vogon Poetry project."""
    type: Literal['fork'] = 'fork'

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step."""
        
        await asyncio.gather(*[
            step.initialize(context)
            for step in self.options.steps
        ])
        return await super().initialize(context)
    
    async def _process_step(self, context: BaseContext) -> Any:
        """Process the fork step."""
        self._logger.info("Processing fork step", steps=len(self.options.steps))
        results = await asyncio.gather(*[
            step.execute(context)
            for step in self.options.steps
        ])
        return await self.merge_results(results)


    async def merge_results(self, results: Sequence[Any]) -> Any:
        self._logger.info("Merging results from forked steps", strategy=self.options.merge_strategy, results=results)
        if self.options.merge_strategy == "concatenate":
            merged = {}
            for result in results:
                for k, v in result.items():
                    merged.setdefault(k, []).append(v)
            return merged

        elif self.options.merge_strategy == "replace":
            return {
                step.output_key or f"step_{i}": result
                for i, (step, result) in enumerate(zip(self.options.steps, results))
            }

        elif self.options.merge_strategy == "prefix":
            merged = {}
            for result in results:
                for k, v in result.items():
                    merged[f"{self.options.prefix}{k}"] = v
            return merged

        raise ValueError(f"Unknown merge strategy: {self.options.merge_strategy}")
