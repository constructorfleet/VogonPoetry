class MergePromptsStep:
    def __init__(self, strategy="concat", input_keys=None):
        self.strategy = strategy
        self.input_keys = input_keys or []

    async def run(self, context):
        values = [context.get(k) for k in self.input_keys]
        if self.strategy == "concat":
            return "\n".join([v for v in values if v])
        elif self.strategy == "json":
            return {f"input_{i}": v for i, v in enumerate(values)}
        else:
            raise ValueError(f"Unknown merge strategy: {self.strategy}")
