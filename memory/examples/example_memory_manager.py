"""
Example Memory Manager v1
Demonstrates region creation, allocation, access, and free.
"""

from memory.manager import MemoryManager

def build_example_memory_manager():
    mm = MemoryManager()

    # Create regions
    mm.create_region("kernel", 500)
    mm.create_region("runtime", 800)
    mm.create_region("sim", 1000)
    mm.create_region("tec", 1200)
    mm.create_region("cognitive", 1500)

    # Allocate
    a1 = mm.allocate("kernel", "boot_state", {"ready": True})
    a2 = mm.allocate("runtime", "event_log", ["routing_init", "substrate_load"]) 
    a3 = mm.allocate("sim", "world_state", {"districts": 3})
    a4 = mm.allocate("tec", "pipeline_cache", {"last": "ok"})
    a5 = mm.allocate("cognitive", "session_data", {"track": "001"})

    # Access
    g1 = mm.get("kernel", "boot_state")
    g2 = mm.get("cognitive", "session_data")

    # Free
    f1 = mm.free("runtime", "event_log")

    return mm, {
        "allocations": [a1, a2, a3, a4, a5],
        "access": [g1, g2],
        "free": f1,
        "describe": mm.describe()
    }
