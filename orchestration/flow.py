"""
Orchestration Flow v1
Defines an ordered orchestration path.
"""

class OrchFlow:
    def __init__(self, name):
        self.name = name
        self.sequence = []

    def add_step(self, node_name):
        self.sequence.append(node_name)

    def describe(self):
        return {
            "name": self.name,
            "sequence": self.sequence
        }
