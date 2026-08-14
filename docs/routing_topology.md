# Routing Topology v1

Portal‑OS routing topology defines:
- Nodes
- Channels
- Links
- Message dispatch
- Failure handling

## Components

### RoutingNode
Represents a routing node in the topology.

### RoutingChannel
Represents a directed channel between nodes.

### RoutingTopology
Stores nodes and channels.

### RoutingEngine
Dispatches messages across the topology.

### Example Topology
Demonstrates how nodes and channels are defined.

See:
- `routing/topology/map.py`
- `routing/topology/engine.py`
- `routing/topology/example_topology.py`
