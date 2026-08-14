"""
Kernel Message Bus v1
Routes messages between kernel subsystems.
"""

class KernelBus:
    def __init__(self):
        self.routes = {}

    def add_route(self, name, handler):
        self.routes[name] = handler

    def send(self, route_name, message):
        handler = self.routes.get(route_name)
        if not handler:
            return {"error": "route_not_found"}
        return handler(message)

    def describe(self):
        return list(self.routes.keys())
