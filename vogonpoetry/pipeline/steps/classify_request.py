"""Request classification step configuration for the pipeline."""
from typing import Annotated, Any, Callable, Literal, MutableSequence, Optional, Sequence, Union, cast
from pydantic import BaseModel, Field

from vogonpoetry.context import BaseContext
from vogonpoetry.embedders.base import BaseEmbedder
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.tags.tag import TTag, Tag, flatten_tags, gather_tags
from vogonpoetry.tags.tag_score import TagScore, cosine_similarity, process_tag
from vogonpoetry.tags.tag_vector import TagVector
from vogonpoetry.logging import logger

ClassifyMethod = Literal['tags', 'embedder']

class ClassifyTagsOptions(BaseModel):
    """Configuration class for tags."""
    method: Literal['tags'] = 'tags'
    tags: Annotated[list[Tag], Field(description="List of tags to classify the request.", default=[])]

class EmbedderClassifyTagsOptions(BaseModel):
    """Configuration class for remote tags."""
    method: Literal['embedder'] = 'embedder'
    tags: Annotated[list[Tag], Field(description="List of tags to classify the request.", default=[])]
    embedder: Annotated[str, Field(description="Embedder name to use for classification.")]
    threshold: Annotated[float, Field(description="Threshold for classification.", default=0.5)]

ClassifyStepOptions = Annotated[
    Union[
        ClassifyTagsOptions,
        EmbedderClassifyTagsOptions,
    ],
    Field(discriminator="method", description="Method to classify the request.")
]

def populate_tag_refs(tag_dict: dict[str, TTag], tag: Tag, typed_tag: TTag) -> dict[str, TTag]:
    """Build a TagVector from a Tag."""
    if tag.parent is not None and tag.parent.id in tag_dict:
        parent = tag_dict[tag.parent.id]
        if parent.sub_tags is None:
            parent.sub_tags = cast(MutableSequence[TTag], []) # type: ignore
        if tag.id not in [t.id for t in parent.sub_tags]: # type: ignore
            parent.sub_tags.append(typed_tag) # type: ignore
        typed_tag.parent = parent # type: ignore
    tag_dict[tag.id] = typed_tag
    return tag_dict

def tag_factory(tags: Sequence[TTag], factory: Callable[[Tag], TTag]) -> dict[str, TTag]:
    """Build a TagVector from a Tag."""
    flattened_tags = flatten_tags(tags)
    vectors = [
        factory(tag)
        for tag
        in flattened_tags
    ]
    tag_vectors: dict[str, TTag] = {
        tag.id: tag
        for tag
        in vectors
    }
    for i, vector in enumerate(vectors):
        tag_vectors = populate_tag_refs(tag_vectors, tags[0], vector)

    return tag_vectors

def vectored_tag_factory(tags: Sequence[TTag], factory: Callable[[Tag], list[float]]) -> dict[str, TagVector]:
    return cast(dict[str, TagVector], tag_factory(tags, lambda t: TagVector(
        vector=factory(t),
        id=t.id,
        name=t.name,
        description=t.description,
        parent=None,
        sub_tags=None,
    )))

def scored_tag_factory(tags: Sequence[TTag], factory: Callable[[Tag], float]) -> dict[str, TagScore]:
    return cast(dict[str, TagScore], tag_factory(tags, lambda t: TagScore(
        score=factory(t),
        id=t.id,
        name=t.name,
        description=t.description,
        parent=None,
        sub_tags=None,
    )))

class ClassifyStep(BaseStep[ClassifyStepOptions, dict[str, TagScore]]):
    """Configuration class for classify request step with tags."""
    type: Literal['classify_request'] = 'classify_request'
    options: ClassifyStepOptions = Field(description="Options for the classify request step.")

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"ClassifyStep-{self.id}")
        self._tagConfigs = gather_tags({}, self.options.tags)
        self._tag_vectors: dict[str, TagVector] = {}
        self._embedder: Optional[BaseEmbedder] = None

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step."""
        if self.options.method == "tags":
            self._logger.info("Initializing classify request step with tags", tags=gather_tags({}, [t for t in self.options.tags]))
            self._tag_vectors = vectored_tag_factory(self.options.tags, lambda _: [])
            return await super().initialize(context)
        elif self.options.embedder is not None and self.options.embedder in context.embedders:
            self._embedder = context.embedders[self.options.embedder]
            self._logger.info("Initializing classify request step with embedder %s", self._embedder.name)
            try:
                self._logger.debug("Initializing classify request step with embedder %s", self._embedder.name)
                keys = list(self._tag_vectors.keys())
                vectors = await self._embedder.embed([self._tag_vectors[t].description for t in keys]) # type: ignore
                self._tag_vectors = {k: TagVector(vector=vector, **self._tag_vectors[k].model_dump()) for k, vector in zip(keys, vectors)}
                self._logger.info("Initialization completed successfully.")
                return await super().initialize(context)
            except Exception as e:
                self._logger.error("Error during initialization: %s", str(e))
                raise
        raise NotImplementedError("Embed method not implemented.")

    async def _process_step(self, context: BaseContext) -> dict[str, TagScore]:
        """Classify the request using the configured method."""
        if self.options.method == "tags":  # Yield control to the event loop
            return scored_tag_factory(self.options.tags, lambda _: 1.0)
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
                    in scored_tag_factory(
                        list(self._tag_vectors.values()),
                        lambda t: cosine_similarity(cast(TagVector, t).vector, vector[0])
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
