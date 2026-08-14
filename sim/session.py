"""
SIM.MODE Session v1
Stateful simulation context.
"""

class SimSession:
    def __init__(self, id_, model_name=None, world_name=None, metadata=None):
        self.id = id_
        self.model_name = model_name
        self.world_name = world_name
        self.metadata = metadata or {}
        self.state = {}
        self.history = []

    def set(self, key, value):
        self.state[key] = value

    def get(self, key, default=None):
        return self.state.get(key, default)

    def record(self, entry):
        self.history.append(entry)

    def describe(self):
        return {
            "id": self.id,
            "model": self.model_name,
            "world": self.world_name,
            "metadata": self.metadata,
            "state": self.state,
            "history": self.history
        }
