from typing import Annotated, Literal

from pydantic import Field
from vogonpoetry.config.embedders.base import BaseEmbedderConfig


class LocalEmbedderConfig(BaseEmbedderConfig):
    """Configuration for local embedder."""
    type: Literal['local'] = "local"
    model: Annotated[str, Field(description="Name of the model to use for embedding.")]
