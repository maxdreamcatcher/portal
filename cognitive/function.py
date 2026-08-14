"""
Cognitive Function v1
Defines a cognitive operation within a domain.
"""

class CognitiveFunction:
    def __init__(self, name, description, executor):
        self.name = name
        self.description = description
        self.executor = executor

    def run(self, session, payload):
        result = self.executor(session, payload)
        return {
            "function": self.name,
            "result": result
        }

    def describe(self):
        return {
            "name": self.name,
            "description": self.description
        }
