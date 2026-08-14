"""
Portal‑OS Shell API Server v1
Simple API server abstraction.
"""

from shell.api.router import ApiRouter

class ApiServer:
    def __init__(self):
        self.router = ApiRouter()

    def add_route(self, path, handler):
        self.router.add_route(path, handler)

    def handle_request(self, path, payload):
        return self.router.dispatch(path, payload)

    def describe(self):
        return self.router.describe()
