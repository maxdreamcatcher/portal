# Class‑C Substrate v1

The Class‑C substrate is the planetary-scale compute layer of Portal‑OS v4.

## Components

### SubstrateNode
Represents a compute node with:
- Load
- Latency
- Health
- Metadata

### SubstrateRegion
Represents a geographic or logical region containing nodes.

### ClassCSubstrate
Stores all regions and nodes.

### SubstrateEngine
Evaluates:
- Node health
- Load balancing
- Substrate alignment

### Example Substrate
Demonstrates how regions and nodes are defined.

See:
- `substrate/class_c/model.py`
- `substrate/class_c/engine.py`
- `substrate/class_c/example_substrate.py`
