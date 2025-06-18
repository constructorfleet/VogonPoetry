"""Context classes for the pipeline."""

from typing import Annotated, Any, Optional
from pydantic import BaseModel, Field

from vogonpoetry.embedders import Embedder
from vogonpoetry.messages.base import BaseMessage
from vogonpoetry.metrics import MetricsCollection


class BaseContext:
    """Base context class for the pipeline."""

    def __init__(
        self,
        visited_steps: list[str] = [],
        data: dict[str, Any] = {},
        messages: list[BaseMessage] = [],
        embedders: dict[str, Embedder] = {},
        tools: list[Any] = [],
        metrics: MetricsCollection = MetricsCollection(),
    ):
        self.visited_steps = visited_steps
        self.data = data
        self.messages = messages
        self.embedders = embedders
        self.tools = tools
        self.metrics = metrics

    # visited_steps: Annotated[
    #     list[str],
    #     Field(description="List of visited step IDs in the pipeline.", default=[]),
    # ]
    # data: Annotated[
    #     dict[str, Any],
    #     Field(description="Arbitrary key-value pairs for the context.", default={}),
    # ]
    # messages: Annotated[
    #     list[BaseMessage[Any]],
    #     Field(description="List of messages in the context.", default=[]),
    # ]
    # embedders: Annotated[
    #     dict[str, Embedder],
    #     Field(description="Embedders associated with the context.", default={}),
    # ]
    # tools: Annotated[
    #     Optional[list[Any]],
    #     Field(description="Tools associated with the context.", default=None),
    # ]
    # metrics: Annotated[
    #     MetricsCollection,
    #     Field(
    #         description="Metrics collection for the context.",
    #         default=MetricsCollection(),
    #     ),
    # ]

    @property
    def latest_message(self) -> Optional[BaseMessage[Any]]:
        """Get the last message from the context."""
        if not self.messages:
            return None
        return self.messages[-1]

    def visit(self, step_id: str) -> None:
        self.visited_steps.append(step_id)

    def has_visited(self, step_id: str) -> bool:
        return step_id in self.visited_steps

    def merge(self, *contexts: "BaseContext", strategy="prefix_keys") -> None:
        if strategy == "prefix_keys":
            for i, ctx in enumerate(contexts):
                for k, v in ctx.data.items():
                    self.data[f"fork_{i}.{k}"] = v
        elif strategy == "overwrite":
            for ctx in contexts:
                self.data.update(ctx.data)
        elif strategy == "deep_merge":
            from collections.abc import Mapping

            def recursive_merge(d1, d2):
                for k, v in d2.items():
                    if (
                        k in d1
                        and isinstance(d1[k], Mapping)
                        and isinstance(v, Mapping)
                    ):
                        recursive_merge(d1[k], v)
                    else:
                        d1[k] = v

            for ctx in contexts:
                recursive_merge(self.data, ctx)
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
