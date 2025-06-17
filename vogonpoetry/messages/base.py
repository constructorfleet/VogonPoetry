"""Base message class for the Vogon Poetry project."""

from typing import Annotated, Generic, TypeVar
from pydantic import BaseModel, Field
from regex import T

TContent = TypeVar("TContent")

class BaseMessage(BaseModel, Generic[TContent]):
    role: Annotated[str, Field(description="Role of the message sender, e.g., 'user', 'system', 'assistant'.")]
    content: Annotated[TContent, Field(description="Content of the message.")]