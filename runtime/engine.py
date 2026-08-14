"""
Runtime Engine v1
Coordinates runtime context, services, and loop.
"""

from runtime.context import RuntimeContext
from runtime.services import RuntimeServices
from runtime.loop import RuntimeLoop

class RuntimeEngine:
    def __init__(self):
        self.context = RuntimeContext()
        self.services = RuntimeServices(self.context)
        self.loop = RuntimeLoop(self.context, self.services)

    def initialize(self):
        self.context.flags["initialized"] = True
        self.services.log("Runtime initialized.")
        return {"status": "runtime_initialized"}

    def start(self):
        self.context.flags["running"] = True
        self.services.log("Runtime started.")
        return {"status": "runtime_started"}

    def register_handler(self, event_name, handler):
        self.loop.register_handler(event_name, handler)

    def emit(self, event_name, payload=None):
        return self.services.emit(event_name, payload)

    def run(self, ticks=1):
        return self.loop.run(ticks)

    def describe(self):
        return self.context.describe()
