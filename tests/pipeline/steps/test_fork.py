import pytest
from typing import Any

from vogonpoetry.context import BaseContext
from vogonpoetry.pipeline.steps.dummy import DummyConfiguration, DummyStep

class DummyLogger:
    def __init__(self):
        self.logs = []
    def info(self, msg, **kwargs):
        self.logs.append((msg, kwargs))

class Step(DummyStep):
    output: Any = None

    async def initialize(self, context):
        self.options.init_called = True
        return None

    async def execute(self, context):
        self.options.process_called = True
        return self.output

@pytest.mark.asyncio
async def test_initialize_calls_all_steps():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        output={"key1": "value1"},
        options=DummyConfiguration(),
    )
    step2 = Step(
        id="step2",
        requires=[],
        type="dummy",
        if_=None,
        output={"key2": "value2"},
        options=DummyConfiguration(),
    )
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        ConcatenateStepOptions,
    )
    options = ConcatenateStepOptions(merge_strategy='concatenate', steps=[step1, step2])
    fork = ForkStep(id="fork1", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    context = BaseContext()
    await fork.initialize(context)
    assert step1.options.init_called
    assert step2.options.init_called

@pytest.mark.asyncio
async def test_process_step_concatenate_merges_results():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        output={"a": 1, "b": 2},
        options=DummyConfiguration()
    )
    step2 = Step(
        id="step2",
        requires=[],
        type="dummy",
        if_=None,
        output={"a": 3, "c": 4},
        options=DummyConfiguration())
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        ConcatenateStepOptions,
    )
    options = ConcatenateStepOptions(steps=[step1, step2])
    fork = ForkStep(id="fork2", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    context = BaseContext()
    result = await fork._process_step(context)
    assert result == {"a": [1, 3], "b": [2], "c": [4]}

@pytest.mark.asyncio
async def test_process_step_replace_merges_results():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        output={"x": 1},
        output_key="foo",
        options=DummyConfiguration()
    )
    step2 = Step(
        id="step2",
        requires=[],
        type="dummy",
        if_=None,
        options=DummyConfiguration(),
        output={"y": 2},
        output_key="bar"
    )
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        ReplaceStepOptions,
    )
    options = ReplaceStepOptions(steps=[step1, step2])
    fork = ForkStep(id="fork3", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    context = BaseContext()
    result = await fork._process_step(context)
    assert result == {"foo": {"x": 1}, "bar": {"y": 2}}

@pytest.mark.asyncio
async def test_process_step_replace_merges_results_with_default_key():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        options=DummyConfiguration(),
        output={"x": 1}
    )
    step2 = Step(
        id="step2",
        requires=[],
        type="dummy",
        options=DummyConfiguration(),
        if_=None,
        output={"y": 2}
    )
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        ReplaceStepOptions,
    )
    options = ReplaceStepOptions(steps=[step1, step2])
    fork = ForkStep(id="fork4", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    context = BaseContext()
    result = await fork._process_step(context)
    assert result == {"step_0": {"x": 1}, "step_1": {"y": 2}}

@pytest.mark.asyncio
async def test_process_step_prefix_merges_results():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        options=DummyConfiguration(),
        output={"a": 1}
    )
    step2 = Step(
        id="step2",
        requires=[],
        type="dummy",
        if_=None,
        options=DummyConfiguration(),
        output={"b": 2}
    )
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        PrefixStepOptions,
    )
    options = PrefixStepOptions(steps=[step1, step2], prefix="pfx_")
    fork = ForkStep(id="fork5", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    context = BaseContext()
    result = await fork._process_step(context)
    assert result == {"pfx_a": 1, "pfx_b": 2}

@pytest.mark.asyncio
async def test_merge_results_unknown_strategy():
    step1 = Step(
        id="step1",
        requires=[],
        type="dummy",
        if_=None,
        options=DummyConfiguration(),
        output={"a": 1}
    )
    from vogonpoetry.pipeline.steps.fork import (
        ForkStep,
        ConcatenateStepOptions,
    )
    options = ConcatenateStepOptions(steps=[step1])
    fork = ForkStep(id="fork6", requires=[], type="fork", if_=None, options=options)
    fork._logger = DummyLogger() # type: ignore
    fork.options.merge_strategy = "unknown"  # type: ignore
    with pytest.raises(ValueError, match="Unknown merge strategy: unknown"):
        await fork.merge_results([{"a": 1}])