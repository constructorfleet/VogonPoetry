"""Request classification step configuration for the pipeline."""
from ast import List
import dis
from typing import Annotated, Any, Dict, Literal, Optional, Union
from click import Option
from pydantic import BaseModel, Field, UrlConstraints
from pydantic_settings import BaseSettings

from vogonpoetry.config.pipeline.steps.base import BaseStepConfig
from vogonpoetry.config.pipeline.tag import TagConfig
from vogonpoetry.pipeline.context import Tag

ClassifyMethod = Literal['tags', 'embedder']

class ClassifyTagsOptions(BaseModel):
    """Configuration class for tags."""
    method: Literal['tags'] = 'tags'
    tags: Annotated[list[TagConfig], Field(description="List of tags to classify the request.", default=[])]

class RemoteClassifyTagsOptions(BaseModel):
    """Configuration class for remote tags."""
    method: Literal['remote'] = 'remote'
    tags: Annotated[list[TagConfig], Field(description="List of tags to classify the request.", default=[])]
    embedder: Annotated[str, Field(description="Embedder name to use for classification.")]
    threshold: Annotated[float, Field(description="Threshold for classification.", default=0.5)]

ClassifyStepOptions = Annotated[
    Union[
        ClassifyTagsOptions,
        RemoteClassifyTagsOptions,
    ],
    Field(discriminator="method", description="Method to classify the request.")
]

class ClassifyStepConfig(BaseStepConfig[ClassifyStepOptions]):
    """Configuration class for classify request step with tags."""
    type: Literal['classify_request'] = 'classify_request'
    options: ClassifyStepOptions = Field(description="Options for the classify request step.")
