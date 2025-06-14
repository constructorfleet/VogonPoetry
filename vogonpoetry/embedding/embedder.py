"""Base class for embedding models."""

import logging


class Embedder:
    def __init__(self, name: str, **kwargs) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__name__}|{name}")
        self.name = name
        pass

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Embed the input texts using the embedder model."""
        raise NotImplementedError("Embed method not implemented.")