"""Types for pipeline steps in the Vogon Poetry project."""
from typing import Annotated, Union

from vogonpoetry.pipeline.steps.classify_request import ClassifyStep
from vogonpoetry.pipeline.steps.merge_prompts import MergePromptsStep


PipelineStep = Union[
    ClassifyStep,
    MergePromptsStep,
]