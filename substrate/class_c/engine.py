"""
Class‑C Substrate Engine v1
Portal‑OS v4

Responsibilities:
- Region management
- Node health evaluation
- Load balancing
- Substrate alignment checks
"""

from substrate.class_c.model import ClassCSubstrate

class SubstrateEngine:
    def __init__(self):
        self.substrate = ClassCSubstrate()

    def add_region(self, name, metadata=None):
        return self.substrate.add_region(name, metadata)

    def add_node(self, region_name, node_name, metadata=None):
        return self.substrate.add_node(region_name, node_name, metadata)

    def evaluate_health(self):
        results = {}
        for region_name, region in self.substrate.regions.items():
            region_health = {}
            for node_name, node in region.nodes.items():
                health = "healthy"
                if node.metrics["load"] > 0.9:
                    health = "overloaded"
                if node.metrics["latency"] > 250:
                    health = "degraded"
                node.set_metric("health", health)
                region_health[node_name] = health
            results[region_name] = region_health
        return results

    def balance_load(self):
        # Simple placeholder load balancing logic
        for region in self.substrate.regions.values():
            for node in region.nodes.values():
                if node.metrics["load"] > 0.9:
                    node.metrics["load"] *= 0.8
        return True

    def describe(self):
        return self.substrate.describe()
