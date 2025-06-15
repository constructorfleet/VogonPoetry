"""Request classification step configuration for the pipeline."""
from ast import List
import dis
from typing import Annotated, Any, Dict, Literal, Optional, Union
from click import Option
from pydantic import BaseModel, Field, UrlConstraints
from pydantic_settings import BaseSettings

from vogonpoetry.config.pipeline.steps.base import BaseStepConfig
from vogonpoetry.config.pipeline.tag import TagConfig

ClassifyMethod = Literal['tags', 'embedder']

class ClassifyRequestStepConfig(BaseStepConfig):
    """Base configuration class for classify request step in the pipeline."""
    type: Literal['classify_request'] = 'classify_request'
    tags: Annotated[list[TagConfig], Field(min_length=1, description="List of tags to classify the request with.")]

class ClassifyWithTagsConfig(ClassifyRequestStepConfig):
    """Configuration class for classify request step with tags."""
    method: Annotated[Literal['tags'], Field('tags', pattern=r'^tags$')]

class ClassifyWithEmbedderConfig(ClassifyRequestStepConfig):
    """Configuration class for classify request step with embedder."""
    method: Annotated[Literal['remote_embeddings'], Field('remote_embeddings', pattern=r'^remote_embeddings$')]
    embedder: Annotated[str, Field(description="Embedder name to use for classification.")]
    threshold: Annotated[float, Field(description="Threshold for classification.", default=0.5)]

ClassifyRequestConfig = Annotated[
    Union[
        ClassifyWithTagsConfig,
        ClassifyWithEmbedderConfig,
    ],
    Field(discriminator="method", description="Method to classify the request.")
]