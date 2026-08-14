"""
Governance API Router v1
Provides API-level governance controls.
"""

class GovernanceApiRouter:
    def __init__(self, lawbook_engine):
        self.lawbook = lawbook_engine
        self.routes = {}

    def add_route(self, path, handler):
        self.routes[path] = handler

    def dispatch(self, path, payload):
        handler = self.routes.get(path)
        if not handler:
            return {"error": "governance_route_not_found"}
        return handler(payload)
