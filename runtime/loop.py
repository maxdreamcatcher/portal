"""
Runtime Loop v1
Main execution loop for Portal‑OS.
"""

class RuntimeLoop:
    def __init__(self, context, services):
        self.context = context
        self.services = services
        self.handlers = {}

    def register_handler(self, event_name, handler):
        self.handlers[event_name] = handler

    def tick(self):
        event = self.services.consume_event()
        if not event:
            return {"status": "idle"}

        handler = self.handlers.get(event["name"])
        if not handler:
            return {"error": "no_handler", "event": event}

        return handler(event)

    def run(self, ticks=1):
        results = []
        for _ in range(ticks):
            results.append(self.tick())
        return results
