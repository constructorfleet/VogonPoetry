"""Pipeline step configuration for the Vogon Poetry project."""
from __future__ import annotations
from typing import Annotated, Union

from pydantic import Field
from vogonpoetry.pipeline.steps.fork_pipeline import ForkStep
from vogonpoetry.pipeline.steps.types import PipelineStep as StepUnion


PipelineStep = Annotated[
    Union[
        StepUnion,
        ForkStep,
    ],
    Field(
        description="Configuration for pipeline steps in the Vogon Poetry project.",
        discriminator="type"
    )
]