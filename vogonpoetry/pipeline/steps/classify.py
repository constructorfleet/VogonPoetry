"""Request classification step configuration for the pipeline."""

from typing import Any, Callable, Generic, Literal, MutableSequence, Optional, Sequence, Union, cast
from pydantic import BaseModel, Field

from vogonpoetry.context import BaseContext
from vogonpoetry.embedders.base import BaseEmbedder
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.tags.tag import Tag
from vogonpoetry.tags.tag_score import TagScore, cosine_similarity, process_tag
from vogonpoetry.tags.tag_vector import TagVector
from vogonpoetry.logging import logger
from vogonpoetry.tags.utils import TagUtilities

# ----- Configuration Models -----

class ClassifyTagsOptions(BaseModel):
    method: Literal['tags'] = 'tags'
    tags: list[Tag] = Field(default_factory=list, description="Tags used for classification.")

class EmbedderClassifyTagsOptions(BaseModel):
    method: Literal['embedder'] = 'embedder'
    tags: list[Tag] = Field(default_factory=list, description="Tags used for classification.")
    embedder: str = Field(description="Embedder name to use.")
    threshold: float = Field(default=0.5, description="Similarity threshold.")

ClassifyStepOptions = Union[ClassifyTagsOptions, EmbedderClassifyTagsOptions]

class ClassifyStep(BaseStep[ClassifyStepOptions, dict[str, TagScore]]):
    """Configuration class for classify request step with tags."""
    type: Literal['classify_request'] = 'classify_request'

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"ClassifyStep-{self.id}")
        self._tagConfigs = TagUtilities[Tag, Tag].gather_tags({}, self.options.tags)
        self._tag_vectors: dict[str, TagVector] = {}
        self._embedder: Optional[BaseEmbedder] = None

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step."""
        if self.options.method == "tags":
            self._logger.info("Initializing classify request step with tags", tags=TagUtilities[Tag, Tag].gather_tags({}, [t for t in self.options.tags]))
            self._tag_vectors = TagUtilities.vectored_tag_map(self.options.tags, lambda _: [])
            return await super().initialize(context)
        elif self.options.embedder is not None and self.options.embedder in context.embedders:
            self._embedder = context.embedders[self.options.embedder]
            self._logger.info("Initializing classify request step with embedder %s", self._embedder.name)
            try:
                self._logger.debug("Initializing classify request step with embedder %s", self._embedder.name)
                keys = list(self._tag_vectors.keys())
                vectors = await self._embedder.embed([self._tag_vectors[t].description for t in keys]) # type: ignore
                self._tag_vectors = {k: TagVector(vector=list(vector), **self._tag_vectors[k].model_dump()) for k, vector in zip(keys, vectors)}
                self._logger.info("Initialization completed successfully.")
                return await super().initialize(context)
            except Exception as e:
                self._logger.error("Error during initialization: %s", str(e))
                raise
        raise NotImplementedError("Embed method not implemented.")

    async def _process_step(self, context: BaseContext) -> dict[str, TagScore]:
        """Classify the request using the configured method."""
        if self.options.method == "tags":  # Yield control to the event loop
            return TagUtilities[Tag, TagScore].scored_tag_map(self.options.tags, lambda _: 1.0)
        elif self.options.method == "embedder" and self._embedder is not None:
            latest_message = context.latest_message
            if latest_message is None or not latest_message.content:
                self._logger.warning("No latest message content found in context.")
                return {}
            content = latest_message.content
            if not content or not isinstance(content, str):
                self._logger.warning("Latest message content is empty or not a string.")
                return {}
            try:
                self._logger.debug("Classifying using embedder %s", self._embedder.name)
                vector = await self._embedder.embed([content])
                scores: dict[str, TagScore] = {
                    id: t
                    for id, t
                    in TagUtilities[TagVector, TagScore].scored_tag_map(
                        list(self._tag_vectors.values()),
                        lambda t: cosine_similarity(cast(TagVector, t).vector, list(vector[0]))
                    ).items()
                    if t.score > self.options.threshold
                }

                for tag in scores.values():
                    if tag.parent is not None and tag.score * 0.8 > tag.parent.score:
                        tag.parent.score = tag.score * 0.8

                return {t.id: t for t in scores.values()}
            except ValueError as e:
                self._logger.error("Value error during classification: %s", str(e))
                raise
        else:
            self._logger.error("Invalid method or embedder not found.", context=context)
            raise ValueError("Invalid method or embedder not found.")
