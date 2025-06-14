"""Pipeline step configuration for the Vogon Poetry project."""

from typing import Annotated, Union

from pydantic import Field

from vogonpoetry.config.pipeline.steps.classify_request import ClassifyRequestStepConfig
from vogonpoetry.config.pipeline.steps.fork import ForkStepConfig
from vogonpoetry.config.pipeline.steps.merge_prompts import MergePromptsStepConfig


StepConfig = Annotated[
    Union[
        ClassifyRequestStepConfig,
        MergePromptsStepConfig,
        ForkStepConfig,
    ],
    Field(
        description="Configuration for pipeline steps in the Vogon Poetry project.",
        discriminator="type"
    )
]