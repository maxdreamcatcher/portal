# Portal‑OS Memory Manager v1

The Memory Manager provides deterministic, governed memory allocation.

## Components

### MemHandle
Safe reference to allocated memory.

### MemRegion
Named memory region with capacity.

### MemPool
Allocator pool for a region.

### MemoryManager
Global allocator + region registry.

### Example
See `memory/examples/example_memory_manager.py`.
