"""Base configuration for pipeline steps."""
from typing import Annotated, ClassVar, Generic, Literal, Optional, TypeVar
from pydantic import BaseModel, Discriminator, Field
from pydantic_settings import BaseSettings

TStepOptions = TypeVar("TStepOptions", bound=BaseModel)

class BaseStepConfig(BaseModel, Generic[TStepOptions]):
    """Base configuration for pipeline steps."""
    id: Optional[str] = Field(description="Unique identifier for the step.", default=None)
    if_: Optional[str] = Field(alias="if", description="Condition to execute the step.", default=None)
    join: Optional[list[str]] = Field(alias="join", description="Ids of the steps to join.", default=None)
    requires: Optional[list[str]] = Field(description="Ids of the steps required for this step.", default=None)
    # fork: Optional[list[list['StepConfig']]] = Field(description="Fork branches for the step.", default=None) # type: ignore
    output_key: Optional[str] = Field(description="Key for the output of the step.", default=None)
    model_config = {
        "populate_by_name": True,
    }