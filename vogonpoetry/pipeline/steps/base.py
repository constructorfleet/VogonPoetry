"""Base configuration for pipeline steps."""
from typing import Any, Generic, Optional, Sequence, TypeVar, Union
from uuid import uuid4
from pydantic import BaseModel, Field
from vogonpoetry.logging import logger
from vogonpoetry.context import BaseContext

TStepOptions = TypeVar("TStepOptions", bound=Union[BaseModel, Sequence[BaseModel]])
TOutput = TypeVar('TOutput')

class BaseStep(BaseModel, Generic[TStepOptions, TOutput]):
    """Base configuration for pipeline steps."""
    id: str = Field(description="Unique identifier for the step.", default_factory=lambda: f"step_{uuid4()}")
    if_: Optional[str] = Field(alias="if", description="Condition to execute the step.", default=None)
    requires: Optional[list[str]] = Field(description="Ids of the steps required for this step.", default=None)
    output_key: Optional[str] = Field(description="Key for the output of the step.", default=None)

    def should_skip(self, context: BaseContext) -> bool:
        """Determine if the step should be skipped based on the context."""
        if self.if_ is None:
            return False
        try:
            return not eval(self.if_, {}, context.data)
        except Exception as e:
            self._logger.error(f"Error evaluating condition '{self.if_}': {e}")
            return True

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"Step-{self.id}")
        return super().model_post_init(context)

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step. This method can be overridden by subclasses."""
        pass

    async def execute(self, context: BaseContext) -> TOutput:
        """Execute the step with the given context."""
        try:
            self._logger.debug("Executing step: %s", self.id)
            return await self._process_step(context)
        except Exception as e:
            self._logger.error("Error executing step %s: %s", self.id, str(e))
            raise

    async def _process_step(self, context: BaseContext) -> TOutput:
        """Process the step. This method can be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")