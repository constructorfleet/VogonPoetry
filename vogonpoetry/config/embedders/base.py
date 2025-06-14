from typing import Annotated

from pydantic import Field


class BaseEmbedderConfig:
    """Base configuration class for all embedder configurations."""
    name: Annotated[str, Field(description="Name of the embedder.")]