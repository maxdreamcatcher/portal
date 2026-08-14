"""
TEC Stage v1
Defines an atomic stage in a TEC pipeline.
"""

class TECStage:
    def __init__(self, name, description, executor):
        self.name = name
        self.description = description
        self.executor = executor

    def run(self, ctx: "TECContext", payload):
        result = self.executor(ctx, payload)
        ctx.record({
            "stage": self.name,
            "payload": payload,
            "result": result
        })
        return {
            "stage": self.name,
            "result": result
        }

    def describe(self):
        return {
            "name": self.name,
            "description": self.description
        }
