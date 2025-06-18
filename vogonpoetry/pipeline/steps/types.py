"""Types for pipeline steps in the Vogon Poetry project."""
from typing import Annotated, Union

from tests.pipeline.steps.test_fork import DummyStep
from vogonpoetry.pipeline.steps.classify import ClassifyStep
from vogonpoetry.pipeline.steps.filter_tools import FilterToolsStep
from vogonpoetry.pipeline.steps.merge_prompts import MergePromptsStep


PipelineStep = Union[
    ClassifyStep,
    MergePromptsStep,
    FilterToolsStep,
    DummyStep,
]