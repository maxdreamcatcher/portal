"""
Signal Handler v1
Synchronous handler for a kernel signal.
"""

class SignalHandler:
    def __init__(self, name, description, executor):
        self.name = name
        self.description = description
        self.executor = executor

    def run(self, signal):
        return self.executor(signal)

    def describe(self):
        return {
            "name": self.name,
            "description": self.description
        }
