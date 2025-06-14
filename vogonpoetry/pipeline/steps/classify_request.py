from ctypes import cast
import itertools
from typing import Annotated, Generic, Optional, Sequence, Tuple, TypeVar, Union

from pydantic import BaseModel, Field
from vogonpoetry.config.pipeline.steps.classify_request import ClassifyRequestConfig, ClassifyWithEmbedderConfig
from vogonpoetry.config.pipeline.tag import TagConfig
from vogonpoetry.pipeline.context import PipelineContext
from vogonpoetry.pipeline.steps.base import PipelineStep

TConfig = TypeVar("TConfig", bound=ClassifyRequestConfig)
TTag = TypeVar("TTag", bound=Union[TagConfig, 'TagVector', 'TagScore'])

class Tag(Generic[TTag], BaseModel):
    """Tag configuration for the pipeline."""
    id: Annotated[str, Field(description="Unique identifier for the tag.")]
    name: Annotated[str, Field(description="Name of the tag.")]
    description: Annotated[str, Field(description="Description of the tag.")]
    sub_tags: Annotated[Optional[Sequence[TTag]], Field(default=None, description="List of sub-tags associated with this tag.")]
    parent: Annotated[Optional[TTag], Field(description="Parent tag, if any.")]

class TagVector(Tag['TagVector']):
    """Tag vector representation for the pipeline."""
    vector: Annotated[list[float], Field(description="Vector representation of the tag.")]


class TagScore(Tag['TagScore']):
    score: Annotated[float, Field(description="Similarity score of the tag.", default=0.0)]

def gather_tags(all_tags: dict[str, TTag], tags: Sequence[TTag], parent: Optional[TTag] = None) -> dict[str, TTag]:
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


class ClassifyRequestStep(Generic[TConfig], PipelineStep[TConfig]):
    def __init__(self, config: TConfig, context: PipelineContext) -> None:
        """Initialize the classify request step."""
        super().__init__(config)

    async def _classify(self, context: PipelineContext) -> set[TagScore]:
        """Classify the request using the configured method."""
        return set([TagScore.model_construct(score=1.0, **t.model_dump()) for t in self.config.tags])

    async def execute(self, context: PipelineContext) -> None:
        """Execute the step with the given context."""
        return await super().execute(context)


class ClassifyRequestStepWithEmbedder(ClassifyRequestStep[ClassifyWithEmbedderConfig]):
    def __init__(self, config: ClassifyWithEmbedderConfig, context: PipelineContext) -> None:
        """Initialize the classify request step with embedder."""
        super().__init__(config, context)
        self.embedder = context.get_embedder(config.embedder)
        self.tag_vectors: dict[str, TagVector] = {
            id: TagVector(vector=[], **tag.model_dump()) for id, tag in gather_tags({}, [t for t in config.tags]).items()
        }

    async def initialize(self) -> None:
        """Initialize the step."""
        try:
            self.logger.debug("Initializing classify request step with embedder %s", self.embedder.name)
            keys = list(self.tag_vectors.keys())
            vectors = await self.embedder.embed([self.tag_vectors[t].description for t in keys])
            self.tag_vectors = {k: TagVector.model_construct(vector=vector, **self.tag_vectors[k].model_dump()) for k, vector in zip(keys, vectors)}
            self.logger.info("Initialization completed successfully.")
        except Exception as e:
            self.logger.error("Error during initialization: %s", str(e))
            raise

    async def _classify(self, context: PipelineContext) -> set[TagScore]:
        """Execute the step with the given context."""
        try:
            self.logger.debug("Classifying using embedder %s", self.embedder.name)
            vector = await self.embedder.embed([context.user_message])
            scores: dict[str, TagScore] = {
                t.id: t
                for t
                in [
                    process_tag(tag, vector[0])
                    for tag
                    in self.tag_vectors.values()
                ]
                if t.score > self.config.threshold
            }

            for tag in scores.values():
                if tag.parent is not None and tag.score * 0.8 > tag.parent.score:
                    tag.parent.score = tag.score * 0.8

            return set([t for t in scores.values() if t.score > self.config.threshold])
        except ValueError as e:
            self.logger.error("Value error during classification: %s", str(e))
            raise