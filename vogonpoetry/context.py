"""Context classes for the pipeline."""


from typing import Annotated, Any, Optional
from pydantic import BaseModel, Field

from vogonpoetry.embedders import Embedder
from vogonpoetry.messages.base import BaseMessage


class BaseContext(BaseModel):
    """Base context class for the pipeline."""

    data: Annotated[dict[str, Any], Field(description="Arbitrary key-value pairs for the context.", default={})]
    messages: Annotated[list[BaseMessage[Any]], Field(description="List of messages in the context.", default=[])]
    embedders: Annotated[dict[str, Embedder], Field(description="Embedders associated with the context.", default={})]

    @property
    def latest_message(self) -> Optional[BaseMessage[Any]]:
        """Get the last message from the context."""
        return self.messages[-1]
    
    def merge(self, *contexts: 'BaseContext', strategy="prefix_keys") -> None:
        if strategy == "prefix_keys":
            for i, ctx in enumerate(contexts):
                for k, v in ctx.data.items():
                    self.data[f"fork_{i}.{k}"] = v
        elif strategy == "overwrite":
            for ctx in contexts:
                self.data.update(ctx)
        elif strategy == "deep_merge":
            from collections.abc import Mapping
            def recursive_merge(d1, d2):
                for k, v in d2.items():
                    if k in d1 and isinstance(d1[k], Mapping) and isinstance(v, Mapping):
                        recursive_merge(d1[k], v)
                    else:
                        d1[k] = v
            for ctx in contexts:
                recursive_merge(self.data, ctx)
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}") 
    