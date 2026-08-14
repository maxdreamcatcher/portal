"""
Kernel State Service v1
Maintains global kernel state for Portal‑OS.
"""

class KernelState:
    def __init__(self):
        self.flags = {
            "booted": False,
            "healthy": True,
            "routing_ready": False,
            "sim_ready": False,
            "tec_ready": False
        }
        self.metadata = {}

    def set_flag(self, key, value):
        self.flags[key] = value

    def get_flag(self, key):
        return self.flags.get(key)

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def describe(self):
        return {
            "flags": self.flags,
            "metadata": self.metadata
        }
