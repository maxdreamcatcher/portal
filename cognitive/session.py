"""
Cognitive Session v1
Holds stateful cognitive context over time.
"""

class CognitiveSession:
    def __init__(self, id_, domain_name, metadata=None):
        self.id = id_
        self.domain_name = domain_name
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
            "domain": self.domain_name,
            "metadata": self.metadata,
            "state": self.state,
            "history": self.history
        }
