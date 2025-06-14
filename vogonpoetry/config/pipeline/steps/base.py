"""Base configuration for pipeline steps."""
from typing import Annotated, Optional
from pydantic import BaseModel, Discriminator, Field
from pydantic_settings import BaseSettings


class BaseStep(BaseModel):
    """Base configuration for pipeline steps."""
    step: Annotated['BaseStep', Field(discriminator="type")]
    id: Annotated[Optional[str], Field(description="Unique identifier for the step.")]
    if_: Annotated[Optional[str], Field("if", description="Condition to execute the step.")]
    join: Annotated[Optional[list[str]], Field("join", description="Ids of the steps to join.")]
    requires: Annotated[Optional[list[str]], Field(description="Ids of the steps required for this step.")]
    fork: Annotated[Optional[list['BaseStep']], Field(description="Fork branches for the step.")]
