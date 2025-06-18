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
    id: str = Field(description="Unique identifier for the step.")
    if_: Optional[str] = Field(serialization_alias="if", description="Condition to execute the step.", default=None)
    requires: Optional[list[str]] = Field(description="Ids of the steps required for this step.", default=None)
    output_key: Optional[str] = Field(description="Key for the output of the step.", default=None)
    options: TStepOptions = Field(description="Options for the step.")

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

    async def _initialize_step(self, context: BaseContext) -> None:
        pass

    async def initialize(self, context: BaseContext) -> None:
        """Initialize the step. This method can be overridden by subclasses."""
        context.metrics.increment("step.initializations", step_id=self.id, step_type=getattr(self, "type", "unknown"))
        with context.metrics.timer("step.initialization_time", step_id=self.id, step_type=getattr(self, "type", "unknown")):
            try:
                await self._initialize_step(context)
            except Exception as e:
                context.metrics.increment("step.initialization_errors", step_id=self.id, step_type=getattr(self, "type", "unknown"), error_type=type(e).__name__)
                self._logger.error("Error initializing step", id=self.id, error=e)
                raise

    async def execute(self, context: BaseContext) -> TOutput:
        """Execute the step with the given context."""
        if context.has_visited(self.id):
            self._logger.warning("Step already been visited. Skipping execution.", id=self.id)
            return context.data.get(self.output_key) if self.output_key else None # type: ignore
        context.metrics.increment("step.invocations", step_id=self.id, step_type=getattr(self, "type", "unknown"))
        context.visit(self.id)
        if self.should_skip(context):
            context.metrics.increment("step.skips", step_id=self.id, step_type=getattr(self, "type", "unknown"))
            self._logger.info("Skipping step due to condition.", id=self.id, condition=self.if_)
            return context.data.get(self.output_key) if self.output_key else None # type: ignore
        try:
            with context.metrics.timer("step.execution_time", step_id=self.id, step_type=getattr(self, "type", "unknown")):
                self._logger.info("Executing step", id=self.id)
                result = await self._process_step(context)
                self._logger.info("Executed step.", id=self.id, result=result)
                return result
        except Exception as e:
            context.metrics.increment("step.execution_errors", step_id=self.id, step_type=getattr(self, "type", "unknown"), error_type=type(e).__name__)
            self._logger.error("Error executing step %s: %s", self.id, str(e))
            raise

    async def _process_step(self, context: BaseContext) -> TOutput:
        """Process the step. This method can be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")