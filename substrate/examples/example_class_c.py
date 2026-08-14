"""
Example Class‑C Substrate v1
Planetary → Oceanic → Orbital → Lunar compute substrate.
"""

from substrate.engine import SubstrateEngine

def build_class_c_substrate():
    engine = SubstrateEngine()
    graph = engine.graph

    # Layers
    planetary = graph.add_layer("planetary", {"scale": "global", "bandwidth": "high"})
    oceanic = graph.add_layer("oceanic", {"scale": "fluid", "bandwidth": "medium"})
    orbital = graph.add_layer("orbital", {"scale": "satellite", "bandwidth": "high"})
    lunar = graph.add_layer("lunar", {"scale": "remote", "bandwidth": "low"})

    # Links
    graph.link("planetary", "oceanic")
    graph.link("oceanic", "orbital")
    graph.link("orbital", "lunar")

    # Resources
    engine.add_resource("planetary_compute", "compute", 1000)
    engine.add_resource("oceanic_memory", "memory", 500)
    engine.add_resource("orbital_storage", "storage", 200)
    engine.add_resource("lunar_compute", "compute", 100)

    # Initialize + activate
    planetary.initialize()
    oceanic.initialize()
    orbital.initialize()
    lunar.initialize()

    planetary.activate()
    oceanic.activate()
    orbital.activate()
    lunar.activate()

    return engine
