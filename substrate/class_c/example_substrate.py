"""
Example Class‑C Substrate v1
Demonstrates how regions and nodes are defined.
"""

from substrate.class_c.engine import SubstrateEngine

def build_example_substrate():
    engine = SubstrateEngine()

    # Add regions
    engine.add_region("north_america", {"class": "C"})
    engine.add_region("europe", {"class": "C"})
    engine.add_region("asia", {"class": "C"})

    # Add nodes
    engine.add_node("north_america", "na-node-1", {"capacity": "high"})
    engine.add_node("north_america", "na-node-2", {"capacity": "medium"})
    engine.add_node("europe", "eu-node-1", {"capacity": "high"})
    engine.add_node("asia", "asia-node-1", {"capacity": "high"})

    # Set example metrics
    na1 = engine.substrate.regions["north_america"].nodes["na-node-1"]
    na1.set_metric("load", 0.95)
    na1.set_metric("latency", 300)

    return engine
