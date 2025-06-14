import asyncio
from pipeline.factory import PipelineFactory
from pipeline.runner import run_pipeline
from pipeline.steps import STEP_REGISTRY
import sys

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/example_pipeline.yaml"
    factory = PipelineFactory(step_registry=STEP_REGISTRY)
    dag = factory.load_from_yaml(config_path)
    context = {}
    asyncio.run(run_pipeline(dag, context))