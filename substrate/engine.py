"""
Substrate Engine v1
Coordinates substrate initialization and activation.
"""

from substrate.graph import SubstrateGraph
from substrate.resource import SubstrateResource

class SubstrateEngine:
    def __init__(self):
        self.graph = SubstrateGraph()
        self.resources = {}

    def add_resource(self, name, type_, capacity):
        res = SubstrateResource(name, type_, capacity)
        self.resources[name] = res
        return res

    def initialize_layer(self, name):
        layer = self.graph.layers.get(name)
        if not layer:
            return {"error": "layer_not_found"}
        return layer.initialize()

    def activate_layer(self, name):
        layer = self.graph.layers.get(name)
        if not layer:
            return {"error": "layer_not_found"}
        return layer.activate()

    def describe(self):
        return {
            "graph": self.graph.describe(),
            "resources": {name: r.describe() for name, r in self.resources.items()}
        }
