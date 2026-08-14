"""
Substrate Resource v1
Defines compute, memory, or storage resources.
"""

class SubstrateResource:
    def __init__(self, name, type_, capacity):
        self.name = name
        self.type = type_
        self.capacity = capacity
        self.allocated = 0

    def allocate(self, amount):
        if self.allocated + amount > self.capacity:
            return {"error": "resource_exceeded"}
        self.allocated += amount
        return {"resource": self.name, "allocated": self.allocated}

    def release(self, amount):
        self.allocated = max(0, self.allocated - amount)
        return {"resource": self.name, "allocated": self.allocated}

    def describe(self):
        return {
            "name": self.name,
            "type": self.type,
            "capacity": self.capacity,
            "allocated": self.allocated
        }
