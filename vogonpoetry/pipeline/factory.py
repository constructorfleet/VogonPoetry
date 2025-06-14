from turtle import st
import yaml
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from vogonpoetry.config.config import Configuration
from vogonpoetry.config.pipeline.pipeline import PipelineConfig
from vogonpoetry.config.pipeline.steps import StepConfig
from vogonpoetry.config.pipeline.steps.base import BaseStepConfig
from vogonpoetry.config.pipeline.steps.fork import ForkStepConfig


class PipelineFactory:
    def __init__(self, step_registry: dict):
        self.registry = step_registry
        self.nodes = {}
        self.edges = {}

    def build(self, config: Configuration):
        return self._build_pipelines(config.pipelines)
    
    def _build_pipelines(self, pipelines: List[PipelineConfig]):
        for pipeline in pipelines:
            if not pipeline.id:
                raise ValueError("Pipeline must have an 'id' field.")
            self._build_graph(pipeline.steps, parent_id=pipeline.id)

    def _build_graph(self, steps: List[StepConfig], parent_id=None):
        for step in steps:
            step_id = step.id or self._gen_anonymous_id()
            self.nodes[step_id] = step

            if step.if_:
                self.nodes[step_id].condition = step.if_

            if step.join:
                for dep in step.join:
                    self.edges.setdefault(dep, []).append(step_id)

            elif step.requires:
                for dep in step.requires:
                    self.edges.setdefault(dep, []).append(step_id)

            elif parent_id:
                self.edges.setdefault(parent_id, []).append(step_id)

            if isinstance(step, ForkStepConfig):
                for fork_branch in step.pipelines:
                    self._build_graph(fork_branch, parent_id=step_id)

        return self._build_topo_sorted_pipeline()

    def _build_topo_sorted_pipeline(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

    def _gen_anonymous_id(self):
        return f"anon_{uuid.uuid4().hex[:8]}"

