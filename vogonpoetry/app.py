import pip
from pydantic import BaseModel, Field
from vogonpoetry.config import Configuration
from vogonpoetry.context import BaseContext
from vogonpoetry.embedders import Embedder, EmbedderTypeAdapter  
from vogonpoetry.messages.base import BaseMessage
from vogonpoetry.pipeline.pipeline import Pipeline



class App:
    def __init__(self, config: Configuration):
        self.config = config
        self.embedders = {embedder.name: EmbedderTypeAdapter.validate_python(embedder) for embedder in config.embedders}
    
    @property
    def pipeline(self) -> Pipeline:
        return self.config.pipeline

    def create_context(self) -> BaseContext:
        return BaseContext(
            visited_steps=[],
            embedders=self.embedders,
            data={},
            messages=[
                BaseMessage(role="system", content="You are a helpful assistant.")
            ]
        )
    
    async def run(self, context: BaseContext) -> BaseContext:
        return await self.pipeline.run(context)


#def build(self, config: Configuration) -> Pipeline:
#         return self._build_pipeline(config.pipeline)
    
#     def _build_pipeline(self, pipeline: Pipeline):
#         if not pipeline.id:
#             raise ValueError("Pipeline must have an 'id' field.")
#         return Pipeline.model_construct(
#             id=pipeline.id,
#             description=pipeline.description,
#             steps=pipeline.steps
#         )
#         return self._build_graph(pipeline.steps, parent_id=pipeline.id)

#     def _build_graph(self, steps: List[StepConfig], parent_id=None):
#         for step in steps:
#             step_id = step.id or self._gen_anonymous_id()
#             self.nodes[step_id] = step.model_construct(**step.model_dump())

#             # if step.if_:
#             #     self.nodes[step_id].condition = step.if_

#             # if step.join:
#             #     for dep in step.join:
#             #         self.edges.setdefault(dep, []).append(step_id)

#             # elif step.requires:
#             #     for dep in step.requires:
#             #         self.edges.setdefault(dep, []).append(step_id)

#             # elif parent_id:
#             #     self.edges.setdefault(parent_id, []).append(step_id)

#             # if step.fork:
#             #     for fork_branch in step.fork:
#             #         self._build_graph(fork_branch, parent_id=step_id)

#         return self._build_topo_sorted_pipeline()

#     def _build_topo_sorted_pipeline(self):
#         return {
#             "nodes": self.nodes,
#             "edges": [] # self.edges
#         }

#     def _gen_anonymous_id(self):
#         return f"anon_{uuid.uuid4().hex[:8]}"

