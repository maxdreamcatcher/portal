"""
SIM.MODE Model v1
Defines a single simulation/model instance.
"""

class SimModel:
    def __init__(self, name, description="", metadata=None, step_fn=None):
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.step_fn = step_fn
        self.state = {}

    def initialize(self, initial_state=None):
        self.state = initial_state or {}
        return {"model": self.name, "status": "initialized", "state": self.state}

    def step(self, context, input_payload=None):
        if not self.step_fn:
            return {"error": "no_step_fn"}
        result = self.step_fn(self.state, context, input_payload)
        self.state = result.get("state", self.state)
        return {
            "model": self.name,
            "result": result,
            "state": self.state
        }

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "state": self.state
        }
