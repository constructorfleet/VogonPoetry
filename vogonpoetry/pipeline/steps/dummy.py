from typing import Any, Awaitable, Callable, Literal, Optional
from pydantic import BaseModel

from vogonpoetry.context import BaseContext
from vogonpoetry.pipeline.steps.base import BaseStep

InitializeFn = Callable[[BaseContext], Awaitable[None]]
ProcessFn = Callable[[BaseContext], Awaitable[Any]]

class DummyConfiguration(BaseModel):
    init_called: bool = False
    process_called: bool = False

class DummyStep(BaseStep[DummyConfiguration, Any]):
    type: Literal['dummy'] = 'dummy'

    async def initialize(self, context: BaseContext) -> None:
        self.options.init_called = True
        return await super().initialize(context)
    
    async def _process_step(self, context: BaseContext) -> Any:
        self.options.process_called = True
        return None