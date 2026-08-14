"""
Kernel Event Service v1
Handles system events and dispatch.
"""

class KernelEvent:
    def __init__(self, name, payload):
        self.name = name
        self.payload = payload

    def describe(self):
        return {
            "event": self.name,
            "payload": self.payload
        }


class KernelEventBus:
    def __init__(self):
        self.handlers = {}

    def register(self, event_name, handler):
        self.handlers[event_name] = handler

    def dispatch(self, event_name, payload):
        handler = self.handlers.get(event_name)
        if not handler:
            return {"error": "event_not_found"}
        event = KernelEvent(event_name, payload)
        return handler(event)
