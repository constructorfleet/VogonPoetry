"""The pipeline context."""
from typing import Annotated, Any, Generic, Optional, Sequence, Union, TypeVar

from pydantic import BaseModel, Field
from vogonpoetry.config.pipeline.tag import TagConfig
from vogonpoetry.embedding.embedder import Embedder

TTag = TypeVar("TTag", bound=Union[TagConfig, 'TagVector', 'TagScore'])
TValue = TypeVar("TValue")

class Tag(BaseModel, Generic[TTag]):
    """Tag configuration for the pipeline."""
    id: Annotated[str, Field(description="Unique identifier for the tag.")]
    name: Annotated[str, Field(description="Name of the tag.")]
    description: Annotated[str, Field(description="Description of the tag.")]
    sub_tags: Annotated[Optional[Sequence[TTag]], Field(default=None, description="List of sub-tags associated with this tag.")]
    parent: Annotated[Optional[TTag], Field(description="Parent tag, if any.")]

class TagVector(Tag['TagVector']):
    """Tag vector representation for the pipeline."""
    vector: Annotated[list[float], Field(description="Vector representation of the tag.")]

class TagScore(Tag['TagScore']):
    score: Annotated[float, Field(description="Similarity score of the tag.", default=0.0)]


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
        self._data: dict[str, Any] ={}

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

    def set(self, key: str, value: Any) -> None:
        """Set a value in the context."""
        self._data[key] = value

    def get(self, key: str, type: TValue) -> TValue:
        return self._data.get(key, None)  # type: ignore
