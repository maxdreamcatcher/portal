"""
MemHandle v1
Safe reference to allocated memory.
"""

class MemHandle:
    def __init__(self, region, key, size):
        self.region = region
        self.key = key
        self.size = size

    def describe(self):
        return {
            "region": self.region,
            "key": self.key,
            "size": self.size
        }
