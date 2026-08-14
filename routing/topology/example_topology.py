"""
Example Routing Topology v1
Demonstrates how routing nodes and channels are defined.
"""

from routing.topology.engine import RoutingEngine

def build_example_topology():
    engine = RoutingEngine()

    # Add nodes
    engine.add_node("kernel", {"type": "system"})
    engine.add_node("identity", {"type": "system"})
    engine.add_node("governance", {"type": "system"})
    engine.add_node("tec", {"type": "system"})
    engine.add_node("sim", {"type": "system"})

    # Add channels
    engine.add_channel("kernel", "identity_update", "identity")
    engine.add_channel("identity", "governance_check", "governance")
    engine.add_channel("governance", "tec_signal", "tec")
    engine.add_channel("sim", "kernel_event", "kernel")

    return engine
