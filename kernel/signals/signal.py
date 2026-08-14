"""
Kernel Signal v1
Represents a synchronous interrupt.
"""

class Signal:
    def __init__(self, name, severity, payload=None, metadata=None):
        self.name = name
        self.severity = severity
        self.payload = payload or {}
        self.metadata = metadata or {}

    def describe(self):
        return {
            "name": self.name,
            "severity": self.severity,
            "payload": self.payload,
            "metadata": self.metadata
        }
