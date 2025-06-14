from uuid import uuid4

_TRACE_STORAGE = {}

def store_trace(context):
    trace_id = str(uuid4())
    _TRACE_STORAGE[trace_id] = context.get("_trace", [])
    return trace_id

def get_trace(trace_id):
    return _TRACE_STORAGE.get(trace_id)
