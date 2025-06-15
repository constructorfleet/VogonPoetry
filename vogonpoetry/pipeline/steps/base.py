"""Base pipeline step implementation for the Vogon Poetry project."""

from typing import Any, Dict, Generic, TypeVar, Union
import logging

from regex import T

from vogonpoetry.config.pipeline.steps import StepConfig
from vogonpoetry.pipeline.context import PipelineContext

logger = logging.getLogger(__name__)

TConfig = TypeVar('TConfig', bound=StepConfig)
TOutput = TypeVar('TOutput')

class PipelineStep(Generic[TConfig, TOutput]):
    """Base class for pipeline steps."""
    def __init__(self, config: TConfig) -> None:
        """Initialize the pipeline step with the given configuration."""
        self.logger = logger.getChild(self.__class__.__name__)
        self.config = config

    async def initialize(self) -> None:
        """Initialize the step. This method can be overridden by subclasses."""
        pass

    async def execute(self, context: PipelineContext) -> TOutput:
        """Execute the step with the given context."""
        try:
            self.logger.debug("Executing step: %s", self.config.id)
            return await self._process_step(context)
        except Exception as e:
            self.logger.error("Error executing step %s: %s", self.config.id, str(e))
            raise

    async def _process_step(self, context: PipelineContext) -> TOutput:
        """Process the step. This method can be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")