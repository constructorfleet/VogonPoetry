
from typing import Annotated

from pydantic import Field
from vogonpoetry.tags.tag import Tag
from vogonpoetry.tags.tag_vector import TagVector


class TagScore(Tag['TagScore']):
    score: Annotated[float, Field(description="Similarity score of the tag.", default=0.0)]

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
        id=tag.id,
        name=tag.name,
        description=tag.description,
        parent=tag.parent,
        sub_tags=tag.sub_tags,
    )