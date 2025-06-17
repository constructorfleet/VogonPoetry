from typing import Annotated

from pydantic import Field
from vogonpoetry.tags.tag import Tag


class TagVector(Tag['TagVector']):
    """Tag vector representation for the pipeline."""
    vector: Annotated[list[float], Field(description="Vector representation of the tag.")]