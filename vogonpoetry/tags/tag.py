"""Base tag configuration for the pipeline."""
from typing import Annotated, Generic, MutableMapping, Optional, Sequence, TypeVar, Union
from pydantic import BaseModel, Field
TTag = TypeVar("TTag", bound='Tag')
TValue = TypeVar("TValue")

class Tag(BaseModel, Generic[TTag]):
    """Tag configuration for the pipeline."""
    id: Annotated[str, Field(description="Unique identifier for the tag.")]
    name: Annotated[str, Field(description="Name of the tag.")]
    description: Annotated[str, Field(description="Description of the tag.")]
    sub_tags: Annotated[Optional[Sequence[TTag]], Field(None, description="List of sub-tags associated with this tag.")]
    parent: Annotated[Optional[TTag], Field(None, description="Parent tag, if any.")]

def gather_tags(all_tags: MutableMapping[str, TTag], tags: Sequence[TTag], parent: Optional[TTag] = None) -> MutableMapping[str, TTag]:
    """Recursively extract tags from a tag object."""
    for tag in tags:
        if isinstance(tag, dict):
            if tag.get("parent") is not None:
                tag["parent"] = all_tags.get(tag["parent"])
                all_tags[tag["id"]] = tag
                if tag.get("sub_tags") is not None:
                    all_tags = gather_tags(all_tags, tag["sub_tags"], tag)
        else:
            if isinstance(tag, Tag) and parent is not None and isinstance(parent, Tag):
                tag.parent = parent # type: ignore
            all_tags[tag.id] = tag
            if tag.sub_tags is not None:
                all_tags = gather_tags(all_tags, tag.sub_tags, tag) # type: ignore
    return all_tags
