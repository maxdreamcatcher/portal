"""
Memory Manager v1
Global allocator + region registry.
"""

from memory.region import MemRegion
from memory.pool import MemPool

class MemoryManager:
    def __init__(self):
        self.regions = {}
        self.pools = {}

    def create_region(self, name, capacity):
        region = MemRegion(name, capacity)
        self.regions[name] = region
        self.pools[name] = MemPool(region)
        return region

    def allocate(self, region_name, key, value):
        pool = self.pools.get(region_name)
        if not pool:
            return {"error": "region_not_found"}
        return pool.allocate(key, value)

    def free(self, region_name, key):
        pool = self.pools.get(region_name)
        if not pool:
            return {"error": "region_not_found"}
        return pool.free(key)

    def get(self, region_name, key):
        pool = self.pools.get(region_name)
        if not pool:
            return {"error": "region_not_found"}
        return pool.get(key)

    def describe(self):
        return {
            "regions": {name: r.describe() for name, r in self.regions.items()},
            "pools": {name: p.describe() for name, p in self.pools.items()}
        }
