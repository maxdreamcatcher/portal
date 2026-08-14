"""
IPC Engine v1
Send/receive/dispatch messages across channels.
"""

from kernel.ipc.registry import IPCRegistry

class IPCEngine:
    def __init__(self):
        self.registry = IPCRegistry()
        self.handlers = {}

    def create_channel(self, name):
        return self.registry.create_channel(name)

    def register_handler(self, channel, type_, handler):
        key = (channel, type_)
        self.handlers[key] = handler

    def send(self, channel, type_, payload, metadata=None):
        ch = self.registry.get_channel(channel)
        if not ch:
            return {"error": "channel_not_found", "channel": channel}
        return ch.send(type_, payload, metadata)

    def dispatch(self, channel):
        ch = self.registry.get_channel(channel)
        if not ch:
            return {"error": "channel_not_found", "channel": channel}

        msg = ch.receive()
        if not msg:
            return {"status": "empty"}

        key = (msg.channel, msg.type)
        handler = self.handlers.get(key)
        if not handler:
            return {"error": "handler_not_found", "message": msg.describe()}

        return handler(msg)

    def describe(self):
        return {
            "channels": self.registry.describe(),
            "handlers": [
                {"channel": c, "type": t}
                for (c, t) in self.handlers.keys()
            ]
        }
