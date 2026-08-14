"""
Runtime Services v1
Provides runtime-level utilities.
"""

class RuntimeServices:
    def __init__(self, context):
        self.context = context

    def log(self, message):
        logs = self.context.get("logs") or []
        logs.append(message)
        self.context.set("logs", logs)
        return {"logged": message}

    def emit(self, event_name, payload=None):
        event = {"name": event_name, "payload": payload}
        self.context.push_event(event)
        return {"event_emitted": event}

    def consume_event(self):
        return self.context.pop_event()
