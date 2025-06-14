"""Base configuration for pipeline steps."""
from typing import Annotated
from pydantic import BaseModel, Discriminator, Field
from pydantic_settings import BaseSettings


class BaseStep(BaseModel):
    """Base configuration for pipeline steps."""
    step: Annotated['BaseStep', Field(discriminator="type")]
