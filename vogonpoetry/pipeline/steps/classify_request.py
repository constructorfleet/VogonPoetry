from ctypes import cast
import itertools
from re import sub
from typing import Annotated, Generic, Mapping, MutableMapping, MutableSequence, Optional, Sequence, Tuple, TypeVar, Union

from pydantic import BaseModel, Field, Tag
from vogonpoetry.config.pipeline.steps.classify_request import ClassifyStepConfig, ClassifyTagsOptions
from vogonpoetry.config.pipeline.tag import TagConfig
from vogonpoetry.embedding.embedder import Embedder
from vogonpoetry.pipeline.context import PipelineContext, TTag, TagScore, TagVector
from vogonpoetry.pipeline.steps.base import PipelineStep


TTag = TypeVar("TTag", bound=Union[TagConfig, TagVector, TagScore])


def gather_tags(all_tags: MutableMapping[str, TTag], tags: Sequence[TTag], parent: Optional[TTag] = None) -> MutableMapping[str, TTag]:
    """Recursively extract tags from a tag object."""
    for tag in tags:
        if isinstance(tag, Tag) and parent is not None and isinstance(parent, Tag):
            tag.parent = parent # type: ignore
        all_tags[tag.id] = tag
        if tag.sub_tags is not None:
            all_tags = gather_tags(all_tags, tag.sub_tags, tag) # type: ignore
    return all_tags


def cosine_similarity(vector1: list[float], vector2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    norm_a = sum(a ** 2 for a in vector1) ** 0.5
    norm_b = sum(b ** 2 for b in vector2) ** 0.5
    return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0


def process_tag(tag: TagVector, user_vector: list[float]) -> TagScore:
    """Process a tag and check if it meets the threshold."""
    similarity = cosine_similarity(tag.vector, user_vector)
    return TagScore.model_construct(
        score=similarity,
        **tag.model_dump()
    )


class ClassifyRequestStep(PipelineStep[ClassifyStepConfig, set[TagScore]]):
    def __init__(self, config: ClassifyStepConfig, context: PipelineContext) -> None:
        """Initialize the classify request step."""
        super().__init__(config)
        self.tagConfigs = gather_tags({}, config.options.tags)
        self.tag_vectors: dict[str, TagVector] = {}
        self.embedder: Optional[Embedder] = None if config.options.method == "tags" else (
            context.get_embedder(config.options.embedder) if config.options.embedder else None
        )

    async def initialize(self) -> None:
        """Initialize the step."""
        if self.config.options.method == "tags":
            self.logger.debug("Initializing classify request step with tags")
            self.tag_vectors: dict[str, TagVector] = {
                id: TagVector.model_construct(vector=[], **tag.model_dump()) for id, tag in gather_tags({}, [t for t in self.config.options.tags]).items()
            }
        elif self.config.options.method == "remote" and self.embedder is not None:
            try:
                self.logger.debug("Initializing classify request step with embedder %s", self.embedder.name)
                keys = list(self.tag_vectors.keys())
                vectors = await self.embedder.embed([self.tag_vectors[t].description for t in keys])
                self.tag_vectors = {k: TagVector.model_construct(vector=vector, **self.tag_vectors[k].model_dump()) for k, vector in zip(keys, vectors)}
                self.logger.info("Initialization completed successfully.")
            except Exception as e:
                self.logger.error("Error during initialization: %s", str(e))
                raise

    async def _process_step(self, context: PipelineContext) -> set[TagScore]:
        """Classify the request using the configured method."""
        if self.config.options.method == "tags":
            return set([TagScore.model_construct(score=1.0, **t.model_dump()) for t in self.config.options.tags])
        elif self.config.options.method == "remote" and self.embedder is not None:
            try:
                self.logger.debug("Classifying using embedder %s", self.embedder.name)
                vector = await self.embedder.embed([context.latest_message.content])
                scores: dict[str, TagScore] = {
                    t.id: t
                    for t
                    in [
                        process_tag(tag, vector[0])
                        for tag
                        in self.tag_vectors.values()
                    ]
                    if t.score > self.config.options.threshold
                }

                for tag in scores.values():
                    if tag.parent is not None and tag.score * 0.8 > tag.parent.score:
                        tag.parent.score = tag.score * 0.8

                return set([t for t in scores.values()])
            except ValueError as e:
                self.logger.error("Value error during classification: %s", str(e))
                raise
        else:
            self.logger.error("Invalid method or embedder not found.")
            raise ValueError("Invalid method or embedder not found.")