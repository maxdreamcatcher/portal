"""
Class‑C Substrate Model v1
Portal‑OS v4

Defines the planetary-scale compute substrate:
- Regions
- Nodes
- Metrics
- Health
- Alignment with Umbrella invariants
"""

class SubstrateNode:
    def __init__(self, name, region, metadata=None):
        self.name = name
        self.region = region
        self.metadata = metadata or {}
        self.metrics = {
            "load": 0.0,
            "latency": 0.0,
            "health": "unknown"
        }

    def set_metric(self, key, value):
        self.metrics[key] = value

    def describe(self):
        return {
            "name": self.name,
            "region": self.region,
            "metadata": self.metadata,
            "metrics": self.metrics
        }


class SubstrateRegion:
    def __init__(self, name, metadata=None):
        self.name = name
        self.metadata = metadata or {}
        self.nodes = {}

    def add_node(self, node: SubstrateNode):
        self.nodes[node.name] = node

    def describe(self):
        return {
            "name": self.name,
            "metadata": self.metadata,
            "nodes": {name: node.describe() for name, node in self.nodes.items()}
        }


class ClassCSubstrate:
    def __init__(self):
        self.regions = {}

    def add_region(self, name, metadata=None):
        region = SubstrateRegion(name, metadata)
        self.regions[name] = region
        return region

    def add_node(self, region_name, node_name, metadata=None):
        region = self.regions.get(region_name)
        if not region:
            return None
        node = SubstrateNode(node_name, region_name, metadata)
        region.add_node(node)
        return node

    def describe(self):
        return {name: region.describe() for name, region in self.regions.items()}
