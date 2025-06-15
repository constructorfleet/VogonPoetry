from typing import Annotated, Literal, Optional

from pydantic import Field
from vogonpoetry.config.embedders.base import BaseEmbedderConfig


class RemoteEmbedderConfig(BaseEmbedderConfig):
    """Configuration for remote embedder."""
    type: Literal['remote'] = "remote"
    model: Annotated[str, Field(description="Name of the model to use for embedding.")]
    url: Annotated[str, Field(description="URL of the remote embedder service.")]
    headers: Annotated[Optional[dict[str, str]], Field(default_factory=dict, description="Headers to include in the request to the remote embedder service.")]
    timeout: Annotated[Optional[int], Field(default=30, description="Timeout for the request to the remote embedder service.")]