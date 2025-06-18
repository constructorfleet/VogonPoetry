from json import tool
import logging
import pytest
from typing import Any, Sequence
from types import SimpleNamespace
from vogonpoetry.context import BaseContext
from vogonpoetry.messages.base import BaseMessage
from vogonpoetry.pipeline.steps import filter_tools as ft_mod

from vogonpoetry.pipeline.steps.filter_tools import (
    FilterToolsStep,
    ContextTagFilterOptions,
    EmbedderSimilarityFilterOptions,
)

class DummyLogger(logging.Logger):
    def __init__(self):
        self.logs = []
    def info(self, msg, **kwargs): # type: ignore
        self.logs.append(('info', msg, kwargs))
    def warning(self, msg, **kwargs): # type: ignore
        self.logs.append(('warning', msg, kwargs))

class Tensor:
    def __init__(self, data):
        self.data = data

    def tolist(self):
        return self.data

class DummyEmbedder:
    def __init__(self, vectors):
        self._vectors = vectors
        self.called_with = None
    async def embed(self, texts, convert_to_tensor=False):
        self.called_with = (texts, convert_to_tensor)
        # Return a list of lists of floats, one per text
        return [v for v in self._vectors]

class DummyTool:
    def __init__(self, tags=None, description="desc"):
        self.tags = tags or []
        self.description = description

@pytest.mark.asyncio
async def test_initialize_embedder_missing(monkeypatch):
    options = EmbedderSimilarityFilterOptions(type='embedder_similarity', embedder='missing', threshold=0.5)
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    context = SimpleNamespace(embedders={})
    with pytest.raises(ValueError, match="Embedder 'missing' not found in context."):
        await step.initialize(context)

@pytest.mark.asyncio
async def test_process_step_context_tag(monkeypatch):
    options = ContextTagFilterOptions(type='context_tag', context_key='mytags')
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    context = BaseContext()
    context.tools = [
        DummyTool(tags=['a', 'b']),
        DummyTool(tags=['c']),
        DummyTool(tags=['b', 'd']),
    ]
    context.data = {'mytags': ['b', 'd']}
    filtered = await step._process_step(context)
    assert len(filtered) == 2
    assert all(any(tag in ['b', 'd'] for tag in tool.tags) for tool in filtered)

@pytest.mark.asyncio
async def test_process_step_context_tag_missing_key():
    options = ContextTagFilterOptions(type='context_tag', context_key='missing')
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    context = BaseContext()
    context.tools = [DummyTool(tags=['a'])]
    context.data = {}
    with pytest.raises(ValueError, match="Context key 'missing' not found in context."):
        await step._process_step(context)

@pytest.mark.asyncio
async def test_process_step_context_tag_no_tools():
    options = ContextTagFilterOptions(type='context_tag', context_key='mytags')
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    context = BaseContext()
    context.tools = []
    context.data = {'mytags': ['a']}
    result = await step._process_step(context)
    assert result == []

@pytest.mark.asyncio
async def test_process_step_embedder_similarity(monkeypatch):
    # Patch cosine_similarity to control output
    monkeypatch.setattr(ft_mod, "cosine_similarity", lambda v1, v2: 0.8 if v1 == [1] else 0.3)
    options = EmbedderSimilarityFilterOptions(type='embedder_similarity', embedder='emb', threshold=0.5)
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    step._embedder = DummyEmbedder([[1], [2], [3]])  # type: ignore
    tool1 = DummyTool(description="desc1")
    tool2 = DummyTool(description="desc2")
    context = BaseContext(
        tools=[tool1, tool2],
        data={'tools': [tool1, tool2]},
        messages=[BaseMessage(role="user", content="msg")], # type: ignore
    )
    filtered = await step._process_step(context)
    assert filtered == [tool1]

@pytest.mark.asyncio
async def test_process_step_embedder_similarity_no_latest_message():
    options = EmbedderSimilarityFilterOptions(type='embedder_similarity', embedder='emb', threshold=0.5)
    step = FilterToolsStep(id="test1", requires=[], type="filter_tools", if_=None, options=options)
    step._logger = DummyLogger() # type: ignore
    step._embedder = DummyEmbedder([[1], [2]]) # type: ignore
    context = BaseContext(
        data={'tools': [DummyTool()]},
        tools=[DummyTool()]
    )
    result = await step._process_step(context)
    assert result == []
