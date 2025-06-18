from typing import Annotated, Any, Literal, Sequence, Union
from pydantic import BaseModel, Field
from vogonpoetry.context import BaseContext
from vogonpoetry.embedders import Embedder
from vogonpoetry.pipeline.steps.base import BaseStep
from vogonpoetry.tags.tag_score import cosine_similarity

class ContextTagFilterOptions(BaseModel):
    """Options for filtering tools based on context tags."""
    type: Literal['context_tag'] = 'context_tag'
    context_key: Annotated[str, Field(description="Key in the context to retrieve tags for filtering.")]

class EmbedderSimilarityFilterOptions(BaseModel):
    """Options for filtering tools based on embedder similarity."""
    type: Literal['embedder_similarity'] = 'embedder_similarity'
    embedder: Annotated[str, Field(description="Key in the context to retrieve the embedder for similarity calculation.")]
    threshold: Annotated[float, Field(description="Similarity threshold for filtering tools.")]

FilterToolsOptions = Annotated[
    Union[
        ContextTagFilterOptions,
        EmbedderSimilarityFilterOptions,
    ],
    Field(discriminator="type", description="Options for filtering tools in the pipeline.")
]


class FilterToolsStep(BaseStep[FilterToolsOptions, Sequence[Any]]):
    """Pipeline step for filtering tools based on specified criteria."""
    type: Literal['filter_tools'] = 'filter_tools'

    async def initialize(self, context: Any) -> None:
        """Initialize the step."""
        self._logger.info("Initializing filter tools step", options=self.options)
        if self.options.type == 'embedder_similarity':
            embedder_key = self.options.embedder
            if embedder_key not in context.embedders:
                raise ValueError(f"Embedder '{embedder_key}' not found in context.")
            self._embedder: Embedder = context.embedders[embedder_key]
        return await super().initialize(context)

    async def _process_step(self, context: BaseContext) -> Sequence[Any]:
        """Run the filter tools step."""
        self._logger.info("Running filter tools step", options=self.options)
        if context.tools is None or len(context.tools) == 0:
            self._logger.warning("No tools found in context.")
            return []
        if self.options.type == 'context_tag':
            context_key = self.options.context_key
            if context_key not in context.data:
                raise ValueError(f"Context key '{context_key}' not found in context.")
            tags = context.data[context_key]
            # Implement filtering logic based on tags
            filtered_tools = [tool for tool in context.tools if any(tag in tool.tags for tag in tags)]
            return filtered_tools
        elif self.options.type == 'embedder_similarity':
            if context.latest_message is None or context.latest_message.content is None:
                self._logger.warning("No latest message or content found in context.")
                return []
            threshold = self.options.threshold
            tools = context.data.get('tools', [])
            texts = [tool.description for tool in tools]
            texts.append(context.latest_message.content)
            vectors = await self._embedder.embed(texts)
            return [
                tool for tool, vector in zip(tools, vectors[:-1])
                if cosine_similarity(vector, vectors[-1]) >= threshold
            ]
        else:
            raise ValueError(f"Unknown filter type: {self.options.type}")