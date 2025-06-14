from typing import Annotated

from pydantic import Field
from vogonpoetry.config.embedders.base import BaseEmbedderConfig


class LocalEmbedderConfig(BaseEmbedderConfig):
    """Configuration for local embedder."""
    type: Annotated[str, Field(description="Type of the embedder.", pattern=r"^local$")]
    model: Annotated[str, Field(description="Name of the model to use for embedding.")]