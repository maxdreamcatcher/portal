"""
Orchestration Node v1
Defines a unit in the orchestration graph.
"""

class OrchNode:
    def __init__(self, name, executor, metadata=None):
        self.name = name
        self.executor = executor
        self.metadata = metadata or {}

    def run(self, context):
        result = self.executor(context)
        return {
            "node": self.name,
            "result": result
        }

    def describe(self):
        return {
            "name": self.name,
            "metadata": self.metadata
        }
