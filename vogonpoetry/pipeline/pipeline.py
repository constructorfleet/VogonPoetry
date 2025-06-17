""""Pipeline configuration for the Vogon Poetry project."""
import inspect
import time
from typing import Any, Optional

from pydantic import BaseModel, Field

from vogonpoetry.logging import logger
from vogonpoetry.context import BaseContext
from vogonpoetry.embedders import Embedder
from vogonpoetry.pipeline.steps import PipelineStep

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


class Pipeline(BaseModel):
    """Base configuration for the pipeline."""
    id: str = Field(description="Identifier of the pipeline.")
    description: Optional[str] = Field(default=None, description="Description of the pipeline.")
    steps: list[PipelineStep] = Field(description="Steps in the pipeline.")

    def model_post_init(self, context: Any) -> None:
        self._logger = logger(f"Pipeline-{self.id}")
        self._nodes: dict[str, PipelineStep] = {
            step.id: step for step in self.steps
        }
        self._edges = {}
        return super().model_post_init(context)

    async def run(self, context: BaseContext):
        visited: set[str] = set()
        # trace_id = context.get("_trace_id")

        def eval_condition(expr, ctx):
            try:
                return eval(expr, {}, ctx)
            except:
                return False

        async def invoke_step(step, ctx, step_id, step_type):
            # counter = metrics.step_counter(step_id)
            # timer = metrics.step_timer(step_id)
            # counter.inc()
            # with timer.time():
            if inspect.iscoroutinefunction(step.execute):
                return await step.execute(ctx)
            else:
                return step.execute(ctx)

        async def run_step(step_id, ctx: BaseContext):
            if step_id in visited:
                return
            visited.add(step_id)

            step = self._nodes[step_id]

            if step.should_skip(ctx):
                self._logger.info("skipping_step", step=step_id, reason="condition_false")
                return

            # if step_cfg.fork:
            #     ctxs = []
            #     logger.info("forking", step=step_id, branches=len(step_cfg.fork))
            #     for i, branch in enumerate(step_cfg.fork):
            #         sub_ctx = PipelineContext(ctx._embedders)
            #         factory = PipelineFactory(STEP_REGISTRY)
            #         fork_dag = factory._build_graph(branch.get("pipeline", []), parent_id=f"{step_id}_fork_{i}")
            #         fork_ctx = await run_pipeline(fork_dag, sub_ctx)
            #         ctxs.append(fork_ctx)
                # ctx.update(merge_contexts(ctxs, strategy="prefix_keys"))

            else:
                self._logger.info("running_step", step=step_id, type=step.type)

                t0 = time.time()
                result = await invoke_step(step, ctx, step.id, step.type)
                t1 = time.time()

                if step.output_key:
                    ctx.data.update({step.output_key: result})
                # ctx.setdefault("_trace", []).append({
                #     "step": step_id,
                #     "type": step_cfg.type,
                #     "output_key": step_cfg.output_key,
                #     "start_time": round(t0, 3),
                #     "end_time": round(t1, 3),
                #     "duration_ms": round((t1 - t0) * 1000, 3),
                #     "keys": list(ctx.keys())
                # })

        try:
            ordered_steps = topological_sort(self._nodes, self._edges)
        except ValueError as e:
            self._logger.error("topology_error", error=str(e))
            raise
        self._logger.info("pipeline_start", pipeline=self.id, steps=ordered_steps)
        for step_id in ordered_steps:
            await run_step(step_id, context)

        # if trace_id:
        #     write_trace(trace_id, context.get("_trace", []))

        return context