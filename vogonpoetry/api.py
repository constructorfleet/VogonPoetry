from fastapi import FastAPI, Request, HTTPException
from uuid import uuid4

from vogonpoetry.loader import load_config
from vogonpoetry.tracing.store import get_trace, store_trace

app = FastAPI()

@app.post("/run")
async def run(request: Request):
    data = await request.json()
    config_path = data.get("config", "config/example_pipeline.yaml")
    context = data.get("context", {})
    trace_id = str(uuid4())
    context["_trace_id"] = trace_id

    # factory = PipelineFactory(step_registry=STEP_REGISTRY)
    # dag = factory.build(load_config(config_path))
    # # configure_metrics(dag.get("metrics", {"backend": "blackhole"}))
    # final_context = await run_pipeline(dag, context)
    # store_trace(final_context)

    return {
        # "context": final_context,
        # "trace_id": trace_id,
        # "trace": final_context.get("_trace", [])
    }

@app.get("/trace/{trace_id}")
async def trace_view(trace_id: str):
    trace = get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace ID not found")
    return {"trace_id": trace_id, "trace": trace}