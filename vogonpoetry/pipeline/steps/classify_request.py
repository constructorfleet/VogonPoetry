class ClassifyRequestStep:
    def __init__(self, model="gpt-3.5"):
        self.model = model

    def run(self, context):
        context["tags"] = ["memory", "tool"]
        return context