"""Request classification step configuration for the pipeline."""
from typing import Annotated, Any, Literal, Optional, Union
from pydantic import BaseModel, Field

from vogonpoetry.context import BaseContext
from vogonpoetry.embedders.base import BaseEmbedder
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.tags.tag import Tag, gather_tags
from vogonpoetry.tags.tag_score import TagScore, process_tag
from vogonpoetry.tags.tag_vector import TagVector
from vogonpoetry.logging import logger

ClassifyMethod = Literal['tags', 'embedder']

class ClassifyTagsOptions(BaseModel):
    """Configuration class for tags."""
    method: Literal['tags'] = 'tags'
    tags: Annotated[list[Tag], Field(description="List of tags to classify the request.", default=[])]

class RemoteClassifyTagsOptions(BaseModel):
    """Configuration class for remote tags."""
    method: Literal['remote'] = 'remote'
    tags: Annotated[list[Tag], Field(description="List of tags to classify the request.", default=[])]
    embedder: Annotated[str, Field(description="Embedder name to use for classification.")]
    threshold: Annotated[float, Field(description="Threshold for classification.", default=0.5)]

ClassifyStepOptions = Annotated[
    Union[
        ClassifyTagsOptions,
        RemoteClassifyTagsOptions,
    ],
    Field(discriminator="method", description="Method to classify the request.")
]

class ClassifyStep(BaseStep[ClassifyStepOptions, dict[str, TagScore]]):
    """Configuration class for classify request step with tags."""
    type: Literal['classify_request'] = 'classify_request'
    options: ClassifyStepOptions = Field(description="Options for the classify request step.")

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"ClassifyStep-{self.id}")
        return super().model_post_init(context)

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step."""
        self.tagConfigs = gather_tags({}, self.options.tags)
        self.tag_vectors: dict[str, TagVector] = {}
        self.embedder: Optional[BaseEmbedder] = None
        if self.options.method == "tags":
            self._logger.debug("Initializing classify request step with tags")
            self.tag_vectors: dict[str, TagVector] = {
                id: TagVector(vector=[], **tag.model_dump()) for id, tag in gather_tags({}, [t for t in self.options.tags]).items()
            }
        elif self.options.method == "remote" and self.embedder is not None and isinstance(self.embedder, BaseEmbedder):
            try:
                self._logger.debug("Initializing classify request step with embedder %s", self.embedder.name)
                keys = list(self.tag_vectors.keys())
                vectors = await self.embedder.embed([self.tag_vectors[t].description for t in keys]) # type: ignore
                self.tag_vectors = {k: TagVector(vector=vector, **self.tag_vectors[k].model_dump()) for k, vector in zip(keys, vectors)}
                self._logger.info("Initialization completed successfully.")
            except Exception as e:
                self._logger.error("Error during initialization: %s", str(e))
                raise

    async def _process_step(self, context: BaseContext) -> dict[str, TagScore]:
        """Classify the request using the configured method."""
        if self.options.method == "tags":
            return {t.id: TagScore(score=1.0, **t.model_dump()) for t in self.options.tags}
        elif self.options.method == "remote" and self.embedder is not None:
            latest_message = context.latest_message
            if latest_message is None or not latest_message.content:
                self._logger.warning("No latest message content found in context.")
                return {}
            content = latest_message.content
            if not content or not isinstance(content, str):
                self._logger.warning("Latest message content is empty or not a string.")
                return {}
            try:
                self._logger.debug("Classifying using embedder %s", self.embedder.name)
                vector = await self.embedder.embed([content])
                scores: dict[str, TagScore] = {
                    t.id: t
                    for t
                    in [
                        process_tag(tag, vector[0])
                        for tag
                        in self.tag_vectors.values()
                    ]
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
            self._logger.error("Invalid method or embedder not found.")
            raise ValueError("Invalid method or embedder not found.")
