"""
IPC Channel v1
FIFO message queue for a specific domain/channel.
"""

from kernel.ipc.message import IPCMessage

class IPCChannel:
    def __init__(self, name):
        self.name = name
        self.queue = []

    def send(self, type_, payload, metadata=None):
        msg = IPCMessage(self.name, type_, payload, metadata)
        self.queue.append(msg)
        return msg

    def receive(self):
        if not self.queue:
            return None
        return self.queue.pop(0)

    def describe(self):
        return {
            "name": self.name,
            "queue_length": len(self.queue)
        }
