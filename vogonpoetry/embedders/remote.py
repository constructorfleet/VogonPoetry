from typing import Annotated, Any, Literal, Optional

import httpx
from pydantic import Field
from vogonpoetry.logging import logger
from vogonpoetry.embedders.base import BaseEmbedder


class RemoteEmbedder(BaseEmbedder):
    """Configuration for remote embedder."""
    type: Literal['remote'] = "remote"
    model: Annotated[str, Field(description="Name of the model to use for embedding.")]
    url: Annotated[str, Field(description="URL of the remote embedder service.")]
    headers: Annotated[Optional[dict[str, str]], Field(default_factory=dict, description="Headers to include in the request to the remote embedder service.")]
    timeout: Annotated[Optional[int], Field(default=30, description="Timeout for the request to the remote embedder service.")]

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"RemoteEmbedder-{self.name}")
        return super().model_post_init(context)

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Embed the input texts using the remote embedder model."""
        self._logger.debug("Classifying using remote embeddings from %s", self.url)
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