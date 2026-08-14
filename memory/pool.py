"""
MemPool v1
Allocator pool that manages handles.
"""

from memory.handle import MemHandle

class MemPool:
    def __init__(self, region: "MemRegion"):
        self.region = region
        self.handles = {}

    def allocate(self, key, value):
        result = self.region.allocate(key, value)
        if "error" in result:
            return result

        handle = MemHandle(self.region.name, key, result["size"])
        self.handles[key] = handle
        return handle.describe()

    def free(self, key):
        result = self.region.free(key)
        if "error" in result:
            return result

        del self.handles[key]
        return result

    def get(self, key):
        return self.region.get(key)

    def describe(self):
        return {
            "region": self.region.name,
            "handles": {k: h.describe() for k, h in self.handles.items()}
        }
