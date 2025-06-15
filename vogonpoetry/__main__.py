import asyncio
from vogonpoetry.config.pipeline.pipeline import PipelineConfig
from vogonpoetry.pipeline.context import PipelineContext
from vogonpoetry.pipeline.factory import PipelineFactory
from vogonpoetry.pipeline.runner import run_pipeline
from vogonpoetry.pipeline.steps import STEP_REGISTRY
import sys

from vogonpoetry.config.loader import load_config

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/example_pipeline.yaml"
    factory = PipelineFactory(step_registry=STEP_REGISTRY)
    dag = factory.build(load_config(config_path))
    context = PipelineContext(dag.get("embedders", {}))
    asyncio.run(run_pipeline(dag, context))