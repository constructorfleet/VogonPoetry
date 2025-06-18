from typing import Annotated, MutableSequence, Sequence

from pydantic import BaseModel, Field


class BaseEmbedder(BaseModel):
    """Base configuration class for all embedder configurations."""
    name: Annotated[str, Field(description="Name of the embedder.")]

    model_config = {
        "populate_by_name": True,
    }

    async def embed(
        self,
        texts: MutableSequence[str],
        **kwargs,
    ) -> MutableSequence[Sequence[float]]:
        """Embed the input texts using the embedder model."""
        raise NotImplementedError("Embed method not implemented.")