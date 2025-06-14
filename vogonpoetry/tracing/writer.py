import os
import json
from pathlib import Path

TRACE_DIR = Path("traces")
TRACE_DIR.mkdir(exist_ok=True)

def cleanup_traces():
    """Delete all traces in the trace directory."""
    # TODO Delete old traces
    raise NotImplementedError("Trace cleanup not implemented yet.")

def write_trace(trace_id, trace_data):
    try:
        with open(TRACE_DIR / f"{trace_id}.json", "w") as f:
            json.dump(trace_data, f, indent=2)
    finally:
        # TODO LOG
        pass

def read_trace(trace_id):
    path = TRACE_DIR / f"{trace_id}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)