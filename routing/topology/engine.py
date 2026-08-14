"""
Routing Engine v1
Portal‑OS v4

Responsible for:
- Message dispatch
- Channel traversal
- Node resolution
- Failure handling
"""

from routing.topology.map import RoutingTopology

class RoutingEngine:
    def __init__(self):
        self.topology = RoutingTopology()

    def add_node(self, name, metadata=None):
        return self.topology.add_node(name, metadata)

    def add_channel(self, source, channel_name, target):
        return self.topology.add_channel(source, channel_name, target)

    def dispatch(self, source, channel_name, message):
        node = self.topology.nodes.get(source)
        if not node:
            return {"error": "source_not_found"}

        # Find channel
        channel = next((c for c in node.channels if c.name == channel_name), None)
        if not channel:
            return {"error": "channel_not_found"}

        target_node = self.topology.nodes.get(channel.target)
        if not target_node:
            return {"error": "target_not_found"}

        # Dispatch message
        return {
            "from": source,
            "to": channel.target,
            "channel": channel_name,
            "message": message,
            "status": "delivered"
        }

    def describe(self):
        return self.topology.describe()
