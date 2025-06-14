from multiprocessing.forkserver import ForkServer
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from vogonpoetry.config.pipeline.steps import StepConfig
from vogonpoetry.config.pipeline.steps.base import BaseStepConfig


class ForkStepConfig(BaseStepConfig):
    """Fork step configuration."""
    type: Annotated[Literal['fork'], Field(description="Type of the step.", pattern=r"^fork$")]
    pipelines: Annotated[list[list[StepConfig]], Field(description="List of pipelines to fork into.", min_length=1)]
