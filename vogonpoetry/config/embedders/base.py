from typing import Annotated

from pydantic import BaseModel, Field


class BaseEmbedderConfig(BaseModel):
    """Base configuration class for all embedder configurations."""
    name: Annotated[str, Field(description="Name of the embedder.")]

    model_config = {
        "populate_by_name": True,
    }