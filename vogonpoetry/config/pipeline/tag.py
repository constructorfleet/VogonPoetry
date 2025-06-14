from typing import Annotated, Optional
from pydantic import BaseModel, Field


class TagConfig(BaseModel):
    id: Annotated[str, Field(description="Unique identifier for the tag.")]
    name: Annotated[str, Field(description="Name of the tag.")]
    description: Annotated[str, Field(description="Description of the tag.")]
    sub_tags: Annotated[Optional[list['TagConfig']], Field(default=None, description="List of sub-tags associated with this tag.")]