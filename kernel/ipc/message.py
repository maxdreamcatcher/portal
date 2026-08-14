"""
IPC Message v1
Typed message object for kernel IPC.
"""

class IPCMessage:
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
