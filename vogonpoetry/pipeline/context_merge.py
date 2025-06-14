def merge_contexts(contexts, strategy="prefix_keys"):
    merged = {}
    if strategy == "prefix_keys":
        for i, ctx in enumerate(contexts):
            for k, v in ctx.items():
                merged[f"fork_{i}.{k}"] = v
    elif strategy == "overwrite":
        for ctx in contexts:
            merged.update(ctx)
    elif strategy == "deep_merge":
        from collections.abc import Mapping
        def recursive_merge(d1, d2):
            for k, v in d2.items():
                if k in d1 and isinstance(d1[k], Mapping) and isinstance(v, Mapping):
                    recursive_merge(d1[k], v)
                else:
                    d1[k] = v
        for ctx in contexts:
            recursive_merge(merged, ctx)
    else:
        raise ValueError(f"Unknown merge strategy: {strategy}")
    return merged