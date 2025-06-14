from typing import Annotated, Literal, Optional

from pydantic import Field

from vogonpoetry.config.pipeline.steps.base import BaseStep


class ForkStep(BaseStep):
    """Fork step configuration."""
    type: Annotated[Literal['fork'], Field(description="Type of the step.", pattern=r"^fork$")]
    pipelines: Annotated[list[list[BaseStep]], Field(description="List of pipelines to fork into.", min_length=1)]