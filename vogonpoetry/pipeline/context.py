"""The pipeline context."""

from typing import Annotated

from pydantic import BaseModel, Field
from vogonpoetry.embedding.embedder import Embedder
from vogonpoetry.pipeline.steps.classify_request import TagScore

class Message(BaseModel):
    """Container for messages in the conversation."""
    role: Annotated[str, Field(description="Role of the message sender.", pattern=r"^(user|assistant|tool)$")]
    content: Annotated[str, Field(description="Content of the message.")]
    tags: Annotated[list[TagScore], Field(description="Tags associated with the message.", default_factory=list)]

class PipelineContext:
    """The context for the pipeline maintaining the state and passing information."""

    def __init__(self, embedders: dict[str, Embedder]) -> None:
        """Initialize the pipeline context."""
        self._embedders: dict[str, Embedder] = embedders
        self._messages: list[Message] = []
        self._user_message: str = ""

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        if role == "user":
            self._user_message = content
        self._messages.append(Message(role=role, content=content, tags=[]))

    def get_embedder(self, name: str) -> Embedder:
        """Get the embedder by name."""
        if name not in self._embedders:
            raise ValueError(f"Embedder {name} not found.")
        return self._embedders[name]
    
    @property
    def user_message(self) -> str:
        """Get the user message."""
        return self._user_message
    
    @property
    def latest_message(self) -> Message:
        """Get the latest message in the conversation."""
        if not self._messages:
            raise ValueError("No messages in the context.")
        return self._messages[-1]

    def set_tags(self, tags: list[TagScore]) -> None:
        """Set the tags for the last message."""
        if not self._messages:
            raise ValueError("No messages in the context.")
        self._messages[-1].tags = tags
