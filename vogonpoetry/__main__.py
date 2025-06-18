import asyncio
from vogonpoetry.app import App
import sys
from vogonpoetry.logging import logger
from vogonpoetry.loader import load_config

_logger = logger(__name__)

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/example_pipeline.yaml"
    app = App(load_config(config_path))
    _logger.info("Pipeline", pipeline=app.pipeline)
    context = app.create_context()

    async def run_app():
        result = await app.run(context)
        _logger.info(f"Pipeline result", result=result)

    asyncio.run(run_app())
    context.metrics.publish_all()
    # context = PipelineContext(dag.get("embedders", {}))
    # asyncio.run(run_pipeline(dag, context))
