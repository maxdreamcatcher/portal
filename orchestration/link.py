"""
Orchestration Link v1
Defines a directed connection between nodes.
"""

class OrchLink:
    def __init__(self, source, target, condition=None, metadata=None):
        self.source = source
        self.target = target
        self.condition = condition
        self.metadata = metadata or {}

    def is_active(self, context, last_result=None):
        if self.condition is None:
            return True
        return self.condition(context, last_result)

    def describe(self):
        return {
            "source": self.source,
            "target": self.target,
            "metadata": self.metadata
        }
