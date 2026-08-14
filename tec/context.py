"""
TEC Context v1
Holds stateful pipeline context.
"""

class TECContext:
    def __init__(self, metadata=None):
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
            "metadata": self.metadata,
            "state": self.state,
            "history": self.history
        }
