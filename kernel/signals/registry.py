"""
Signal Registry v1
Stores all signal handlers.
"""

from kernel.signals.handler import SignalHandler

class SignalRegistry:
    def __init__(self):
        self.handlers = {}

    def register(self, signal_name, handler: SignalHandler):
        self.handlers[signal_name] = handler

    def get(self, signal_name):
        return self.handlers.get(signal_name)

    def describe(self):
        return {
            "handlers": {
                name: handler.describe()
                for name, handler in self.handlers.items()
            }
        }
