"""
Kernel Module Registry v1
Tracks loaded modules and their status.
"""

class ModuleRegistry:
    def __init__(self):
        self.modules = {}

    def register(self, name):
        self.modules[name] = {"status": "loaded"}
        return True

    def status(self, name):
        return self.modules.get(name, None)
