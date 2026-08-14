"""
Cognitive Domain v1
Defines a named cognitive space in Portal‑OS.
"""

class CognitiveDomain:
    def __init__(self, name, description="", metadata=None):
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.functions = {}

    def register_function(self, func):
        self.functions[func.name] = func

    def get_function(self, name):
        return self.functions.get(name)

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "functions": list(self.functions.keys())
        }
