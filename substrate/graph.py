"""
Substrate Graph v1
Defines multi-layer substrate topology.
"""

from substrate.layer import SubstrateLayer

class SubstrateGraph:
    def __init__(self):
        self.layers = {}
        self.links = []

    def add_layer(self, name, config=None):
        layer = SubstrateLayer(name, config)
        self.layers[name] = layer
        return layer

    def link(self, source, target):
        self.links.append({"source": source, "target": target})

    def describe(self):
        return {
            "layers": {name: layer.describe() for name, layer in self.layers.items()},
            "links": self.links
        }
