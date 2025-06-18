""" "Pipeline configuration for the Vogon Poetry project."""

import asyncio
import time
from typing import Any, Optional

from pymetrics.instruments import Counter, Timer
from pydantic import BaseModel, Field

from vogonpoetry.logging import logger
from vogonpoetry.context import BaseContext
from vogonpoetry.embedders import Embedder
from vogonpoetry.pipeline.steps import PipelineStep
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.pipeline.steps.fork import ForkStep

_logger = logger("topological_sort")


def topological_sort(nodes: dict[str, PipelineStep], edges):
    from collections import defaultdict, deque

    in_degree = defaultdict(int)
    graph = defaultdict(list)

    for src, targets in edges.items():
        for tgt in targets:
            graph[src].append(tgt)
            in_degree[tgt] += 1
    _logger.info("Graph", graph=graph, in_degree=dict(in_degree))
    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []
    while queue:
        _logger.info("Queue", queue=list(queue))
        node = queue.popleft()
        _logger.info("Visiting node", node=node)
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(result) != len(nodes):
        raise ValueError("Cycle detected in pipeline graph")

    return result


async def run_steps(
    self, context: BaseContext, steps: list[PipelineStep]
) -> BaseContext:
    # trace_id = context.get("_trace_id")

    def eval_condition(expr, ctx):
        try:
            return eval(expr, {}, ctx)
        except:
            return False
    async def run_step(step: PipelineStep, ctx: BaseContext) -> BaseContext:
        self._logger.info("running_step", step=step.id, type=step.type)
        result = await step.execute(ctx)

        if step.output_key:
            ctx.data.update({step.output_key: result})
        return ctx

    try:
        topological_sort(self._nodes, self._edges)
    except ValueError as e:
        self._logger.error("topology_error", error=str(e))
        raise
    self._logger.info("pipeline_start", pipeline=self.id, steps=self.steps)
    for step in self.steps:
        context = await run_step(step, context)

    # if trace_id:
    #     write_trace(trace_id, context.get("_trace", []))

    return context


class Pipeline(BaseModel):
    """Base configuration for the pipeline."""

    id: str = Field(description="Identifier of the pipeline.")
    description: Optional[str] = Field(
        default=None, description="Description of the pipeline."
    )
    steps: list[PipelineStep] = Field(description="Steps in the pipeline.")

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"Pipeline-{self.id}")
        self._nodes: dict[str, PipelineStep] = {step.id: step for step in self.steps}
        self._edges: dict[str, set[str]] = {step.id: set() for step in self.steps}

        def collect_edges(parent_step):
            if hasattr(parent_step.options, "steps"):
                for child in parent_step.options.steps:
                    self._edges[parent_step.id].add(child.id)
                    if child.id not in self._nodes:
                        self._nodes[child.id] = child
                    if child.id not in self._edges:
                        self._edges[child.id] = set()

        for step in self.steps:
            collect_edges(step)

        step_ids = list(self._nodes.keys())
        dupes = set([x for x in step_ids if step_ids.count(x) > 1])
        if dupes:
            raise ValueError(f"Duplicate step IDs found (after namespacing?): {dupes}")

    async def run(self, context: BaseContext) -> BaseContext:
        """Run the pipeline with the given context."""
        with context.metrics.timer("pipeline.process_time", pipeline_id=self.id):
            with context.metrics.timer("pipeline.initialization_time", pipeline_id=self.id):
                await asyncio.gather(*[step.initialize(context) for step in self.steps])
            with context.metrics.timer("pipeline.execution_time", pipeline_id=self.id):
                return await run_steps(self, context, self.steps)
