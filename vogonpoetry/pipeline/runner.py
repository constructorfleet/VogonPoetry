import asyncio
import inspect
import time
from pipeline.steps import STEP_REGISTRY
from pipeline.context_merge import merge_contexts
from pipeline.factory import PipelineFactory
from pipeline.logging import logger
from pipeline.metrics import metrics
from pipeline.topo import topological_sort
from pipeline.trace_writer import write_trace


async def run_pipeline(dag, context):
    visited = set()
    trace_id = context.get("_trace_id")

    def eval_condition(expr, ctx):
        try:
            return eval(expr, {}, ctx)
        except:
            return False

    async def invoke_step(step, ctx, step_id, step_type):
        counter = metrics.step_counter(step_id)
        timer = metrics.step_timer(step_id)
        counter.inc()
        with timer.time():
            if inspect.iscoroutinefunction(step.run):
                return await step.run(ctx)
            else:
                return step.run(ctx)

    async def run_step(step_id, ctx):
        if step_id in visited:
            return
        visited.add(step_id)

        step_cfg = dag["nodes"][step_id]

        if hasattr(step_cfg, "if_") and step_cfg.if_:
            if not eval_condition(step_cfg.if_, ctx):
                logger.info("skipping_step", step=step_id, reason="condition_false")
                return

        if step_cfg.fork:
            ctxs = []
            logger.info("forking", step=step_id, branches=len(step_cfg.fork))
            for i, branch in enumerate(step_cfg.fork):
                sub_ctx = dict(ctx)
                factory = PipelineFactory(STEP_REGISTRY)
                fork_dag = factory._build_graph(branch.get("pipeline", []), parent_id=f"{step_id}_fork_{i}")
                fork_ctx = await run_pipeline(fork_dag, sub_ctx)
                ctxs.append(fork_ctx)
            ctx.update(merge_contexts(ctxs, strategy="prefix_keys"))

        elif step_cfg.type:
            step_cls = STEP_REGISTRY[step_cfg.type]
            step = step_cls(**step_cfg.config)
            logger.info("running_step", step=step_id, type=step_cfg.type)

            t0 = time.time()
            result = await invoke_step(step, ctx, step_id, step_cfg.type)
            t1 = time.time()

            if step_cfg.output_key:
                ctx[step_cfg.output_key] = result
            ctx.setdefault("_trace", []).append({
                "step": step_id,
                "type": step_cfg.type,
                "output_key": step_cfg.output_key,
                "start_time": round(t0, 3),
                "end_time": round(t1, 3),
                "duration_ms": round((t1 - t0) * 1000, 3),
                "keys": list(ctx.keys())
            })

    try:
        ordered_steps = topological_sort(dag["nodes"], dag["edges"])
    except ValueError as e:
        logger.error("topology_error", error=str(e))
        raise

    for step_id in ordered_steps:
        await run_step(step_id, context)

    if trace_id:
        write_trace(trace_id, context.get("_trace", []))

    return context