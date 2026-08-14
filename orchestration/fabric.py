"""
Orchestration Fabric v1
Global orchestration graph for Portal‑OS.
"""

from orchestration.node import OrchNode
from orchestration.link import OrchLink
from orchestration.flow import OrchFlow

class OrchFabric:
    def __init__(self):
        self.nodes = {}
        self.links = []
        self.flows = {}

    def add_node(self, name, executor, metadata=None):
        node = OrchNode(name, executor, metadata)
        self.nodes[name] = node
        return node

    def add_link(self, source, target, condition=None, metadata=None):
        link = OrchLink(source, target, condition, metadata)
        self.links.append(link)
        return link

    def add_flow(self, name):
        flow = OrchFlow(name)
        self.flows[name] = flow
        return flow

    def get_node(self, name):
        return self.nodes.get(name)

    def describe(self):
        return {
            "nodes": {name: n.describe() for name, n in self.nodes.items()},
            "links": [l.describe() for l in self.links],
            "flows": {name: f.describe() for name, f in self.flows.items()}
        }
