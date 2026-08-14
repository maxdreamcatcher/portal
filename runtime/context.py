"""
Runtime Context v1
Holds global runtime state for Portal‑OS.
"""

class RuntimeContext:
    def __init__(self):
        self.state = {}
        self.events = []
        self.flags = {
            "running": False,
            "initialized": False
        }

    def set(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)

    def push_event(self, event):
        self.events.append(event)

    def pop_event(self):
        if not self.events:
            return None
        return self.events.pop(0)

    def describe(self):
        return {
            "state": self.state,
            "events": self.events,
            "flags": self.flags
        }
