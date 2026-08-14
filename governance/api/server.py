"""
Governance API Server v1
Simple governance API abstraction.
"""

from governance.api.router import GovernanceApiRouter

class GovernanceApiServer:
    def __init__(self, lawbook_engine):
        self.router = GovernanceApiRouter(lawbook_engine)

    def add_route(self, path, handler):
        self.router.add_route(path, handler)

    def handle(self, path, payload):
        return self.router.dispatch(path, payload)

    def describe(self):
        return list(self.router.routes.keys())
