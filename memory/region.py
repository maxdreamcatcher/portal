"""
MemRegion v1
Named memory region with its own storage and limits.
"""

class MemRegion:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.used = 0
        self.storage = {}

    def allocate(self, key, value):
        size = len(str(value))
        if self.used + size > self.capacity:
            return {"error": "region_capacity_exceeded", "region": self.name}

        self.storage[key] = value
        self.used += size
        return {"region": self.name, "key": key, "size": size}

    def free(self, key):
        if key not in self.storage:
            return {"error": "key_not_found"}

        size = len(str(self.storage[key]))
        del self.storage[key]
        self.used -= size
        return {"region": self.name, "key": key, "freed": size}

    def get(self, key):
        return self.storage.get(key)

    def describe(self):
        return {
            "name": self.name,
            "capacity": self.capacity,
            "used": self.used,
            "keys": list(self.storage.keys())
        }
