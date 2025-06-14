"""Base configuration for pipeline steps."""
from typing import Annotated
from pydantic import Discriminator, Field
from pydantic_settings import BaseSettings


class BaseStep(BaseSettings):
    """Base configuration for pipeline steps."""
    step: Annotated['BaseStep', Field(discriminator="type")]
