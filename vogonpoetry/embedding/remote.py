"""Embedder class for handling text embedding."""

from typing import Any
import httpx
from vogonpoetry.embedding.embedder import Embedder


class RemoteEmbedder(Embedder):
    """
    A class to handle remote embedding using a specified model.
    """

    def __init__(
            self,
            name: str,
            model: str,
            url: str,
            headers: dict[str, str] | None = None,
            timeout: int | None = None,
    ) -> None:
        """Initialize the remote embedder with a model name and URL."""
        super().__init__(name)
        self.model = model
        self.url = url
        self.headers = headers
        self.timeout = timeout
        

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Embed the input texts using the remote embedder model."""
        self.logger.debug("Classifying using remote embeddings from %s", self.url)
        payload: dict[str, Any] = {"input": texts}
        headers: dict[str, str] = self.headers or {}
        timeout: int = self.timeout or 30

        if self.model:
            payload["model"] = self.model

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])