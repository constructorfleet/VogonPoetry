"""Base pipeline step implementation for the Vogon Poetry project."""

from typing import Any, Dict, Generic, TypeVar, Union
import logging

from vogonpoetry.config.pipeline.steps import StepConfig
from vogonpoetry.pipeline.context import PipelineContext

logger = logging.getLogger(__name__)

TConfig = TypeVar('TConfig', bound=StepConfig)

class PipelineStep(Generic[TConfig]):
    """Base class for pipeline steps."""
    def __init__(self, config: TConfig) -> None:
        """Initialize the pipeline step with the given configuration."""
        self.logger = logger.getChild(self.__class__.__name__)
        self.config = config

    async def initialize(self) -> None:
        """Initialize the step. This method can be overridden by subclasses."""
        pass

    async def execute(self, context: PipelineContext) -> None:
        """Execute the step with the given context."""
        raise NotImplementedError("Subclasses must implement this method.")