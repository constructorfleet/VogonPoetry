"""Request classification step configuration for the pipeline."""
from ast import List
import dis
from typing import Annotated, Any, Dict, Literal, Optional
from click import Option
from pydantic import BaseModel, Field, UrlConstraints
from pydantic_settings import BaseSettings

from vogonpoetry.config.pipeline.steps.base import BaseStep

class ClassifyRequestStepConfig(BaseStep):
    """Base configuration class for classify request step in the pipeline."""
    type: Annotated[Literal['classify_request'], Field('classify_request', pattern=r'^classify_request$')]

class ClassifyWithTags(ClassifyRequestStepConfig):
    """Configuration class for classify request step with tags."""
    tags: Annotated[list[str], Field(min_length=1, description="List of tags to classify the request with.")]

class ClassifyWithRemoteEmbeddings(ClassifyRequestStepConfig):
    """Configuration class for classify request step with remote embeddings."""
    url: Annotated[str, Field(description="The url for remote embeddings"), UrlConstraints(default_path="/v1/embeddings")]
    model: Annotated[Optional[str], Field(default=None, description="Model to use for classification.")]
    headers: Annotated[Optional[Dict[str, str]], Field(default=None, description="Headers to include in the request.")]
    timeout: Annotated[Optional[int], Field(default=30, description="Timeout for the request in seconds.")]

class ClassifyWithLocalEmbeddings(ClassifyRequestStepConfig):
    """Configuration class for classify request step with local embeddings via sentence transformers."""
    model: Annotated[str, Field(description="Model to use for classification.")]