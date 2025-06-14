import yaml
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StepConfig(BaseModel):
    id: Optional[str]
    type: Optional[str]
    config: Dict[str, Any] = {}
    output_key: Optional[str]
    input_keys: Optional[Dict[str, str]] = None
    requires: Optional[List[str]] = None
    if_: Optional[str] = None
    fork: Optional[List[Dict[str, Any]]] = None
    join: Optional[List[str]] = None

class PipelineSpec(BaseModel):
    name: str
    description: Optional[str]
    pipeline: List[StepConfig]

class PipelineFactory:
    def __init__(self, step_registry: dict):
        self.registry = step_registry
        self.nodes = {}
        self.edges = {}

    def load_from_yaml(self, yaml_path: str):
        with open(yaml_path) as f:
            raw = yaml.safe_load(f)
        spec = PipelineSpec(**raw)
        return self._build_graph(spec.pipeline)

    def _build_graph(self, steps: List[StepConfig], parent_id=None):
        for step_dict in steps:
            step_cfg = StepConfig(**step_dict) if isinstance(step_dict, dict) else step_dict
            step_id = step_cfg.id or self._gen_anonymous_id()
            self.nodes[step_id] = step_cfg

            if step_cfg.if_:
                self.nodes[step_id].condition = step_cfg.if_

            if step_cfg.join:
                for dep in step_cfg.join:
                    self.edges.setdefault(dep, []).append(step_id)

            elif step_cfg.requires:
                for dep in step_cfg.requires:
                    self.edges.setdefault(dep, []).append(step_id)

            elif parent_id:
                self.edges.setdefault(parent_id, []).append(step_id)

            if step_cfg.fork:
                for fork_branch in step_cfg.fork:
                    subpipeline = fork_branch.get("pipeline", [])
                    self._build_graph(subpipeline, parent_id=step_id)

        return self._build_topo_sorted_pipeline()

    def _build_topo_sorted_pipeline(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

    def _gen_anonymous_id(self):
        return f"anon_{uuid.uuid4().hex[:8]}"

