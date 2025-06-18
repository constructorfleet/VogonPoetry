from typing import Annotated, Any, Literal
from sentence_transformers import SentenceTransformer
from pydantic import Field
from vogonpoetry.logging import logger
from vogonpoetry.embedders.base import BaseEmbedder


class LocalEmbedder(BaseEmbedder):
    """Configuration for local embedder."""
    type: Literal['local'] = "local"
    model_name: Annotated[str, Field(description="Name of the model to use for embedding.")]

    def model_post_init(self, context: Any) -> None:
        """Initialize the sentence transformer model."""
        self._model = SentenceTransformer(self.model_name)
        self._logger = logger(f"LocalEmbedder-{self.name}")

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Embed the input texts using the sentence transformer model."""
        self._logger.debug("Classifying using local embeddings with model %s", self.model_name)
        encodings = self._model.encode(texts, convert_to_tensor=False)
        if not isinstance(encodings, list):
            return [encodings.tolist()]
        return [
            encoding.tolist()
            for encoding
            in encodings
        ]