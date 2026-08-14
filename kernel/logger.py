"""
Kernel Logger v1
Simple logging system for Portal‑OS kernel events.
"""

class KernelLogger:
    def __init__(self):
        self.events = []

    def log(self, message):
        self.events.append(message)
        return True

    def dump(self):
        return self.events
