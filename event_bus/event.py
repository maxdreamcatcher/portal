"""
Event v1
Represents a broadcast event.
"""

class Event:
    def __init__(self, channel, type_, payload, metadata=None):
        self.channel = channel
        self.type = type_
        self.payload = payload
        self.metadata = metadata or {}

    def describe(self):
        return {
            "channel": self.channel,
            "type": self.type,
            "payload": self.payload,
            "metadata": self.metadata
        }
