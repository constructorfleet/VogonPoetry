import os
import json
from pathlib import Path

TRACE_DIR = Path("traces")
TRACE_DIR.mkdir(exist_ok=True)

def write_trace(trace_id, trace_data):
    with open(TRACE_DIR / f"{trace_id}.json", "w") as f:
        json.dump(trace_data, f, indent=2)

def read_trace(trace_id):
    path = TRACE_DIR / f"{trace_id}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)