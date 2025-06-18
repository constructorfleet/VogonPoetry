"""Base tag configuration for the pipeline."""
import json
from typing import Annotated, Generic, MutableSequence, Optional, TypeVar
from pydantic import BaseModel, Field, model_serializer

TTag = TypeVar("TTag", bound='Tag')
TValue = TypeVar("TValue")

class Tag(BaseModel, Generic[TTag]):
    """Tag configuration for the pipeline."""
    id: Annotated[str, Field(description="Unique identifier for the tag.")]
    name: Annotated[str, Field(description="Name of the tag.")]
    description: Annotated[str, Field(description="Description of the tag.")]
    sub_tags: Annotated[Optional[MutableSequence[TTag]], Field(None, description="List of sub-tags associated with this tag.")]
    parent: Annotated[Optional[TTag], Field(None, description="Parent tag, if any.")]

    @model_serializer
    def ser_model(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent": self.parent.id if self.parent else None,
            "sub_tags": [sub_tag.ser_model() for sub_tag in self.sub_tags] if self.sub_tags else None,
        }, default=str)
