"""Embedder using sentence transformer to get embeddings."""

from typing import Any, Dict, List, Optional, Union
from sentence_transformers import SentenceTransformer
from vogonpoetry.embedding.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    """Embedder using sentence transformer to get embeddings."""

    def __init__(self, model_name: str, **kwargs: Any) -> None:
        """Initialize the embedder with a model name and optional parameters."""
        super().__init__(model_name=model_name, **kwargs)
        self.model = SentenceTransformer(model_name)

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Embed the input texts using the sentence transformer model."""
        self.logger.debug("Classifying using local embeddings with model %s", self.model)
        encodings = self.model.encode(texts, convert_to_tensor=False)
        if not isinstance(encodings, list):
            return [encodings.tolist()]
        return [
            encoding.tolist()
            for encoding
            in encodings
        ]