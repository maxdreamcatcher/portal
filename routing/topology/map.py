"""
Routing Topology Map v1
Portal‑OS v4

Defines the global routing topology used by Portal‑OS:
- Nodes
- Channels
- Links
- Topology graph
"""

class RoutingNode:
    def __init__(self, name, metadata=None):
        self.name = name
        self.metadata = metadata or {}
        self.channels = []

    def add_channel(self, channel):
        self.channels.append(channel)

    def describe(self):
        return {
            "name": self.name,
            "metadata": self.metadata,
            "channels": [c.name for c in self.channels]
        }


class RoutingChannel:
    def __init__(self, name, target):
        self.name = name
        self.target = target  # target node name

    def describe(self):
        return {
            "name": self.name,
            "target": self.target
        }


class RoutingTopology:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, metadata=None):
        node = RoutingNode(name, metadata)
        self.nodes[name] = node
        return node

    def add_channel(self, source, channel_name, target):
        if source not in self.nodes or target not in self.nodes:
            return False
        channel = RoutingChannel(channel_name, target)
        self.nodes[source].add_channel(channel)
        return True

    def describe(self):
        return {name: node.describe() for name, node in self.nodes.items()}
