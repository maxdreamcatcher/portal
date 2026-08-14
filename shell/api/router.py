"""
Portal‑OS Shell API Router v1
Routes API calls to handlers.
"""

class ApiRouter:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler):
        self.routes[path] = handler

    def dispatch(self, path, payload):
        handler = self.routes.get(path)
        if not handler:
            return {"error": "route_not_found"}
        return handler(payload)

    def describe(self):
        return list(self.routes.keys())
