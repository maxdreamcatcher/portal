"""
City Systems World v1
Example SIM.MODE world for urban flows.
"""

from sim.world import SimWorld

def build_city_world(engine):
    world = SimWorld(
        "city_world",
        "Urban system world with districts and flows.",
        {"category": "systems"}
    )

    # Entities
    world.add_entity("district_A", {"population": 1000, "load": 0.3})
    world.add_entity("district_B", {"population": 800, "load": 0.5})
    world.add_entity("district_C", {"population": 1200, "load": 0.7})

    # Rules
    def flow_rule(entities, context):
        factor = context.get("flow_factor", 1.0)
        for e in entities.values():
            e["load"] = min(1.0, e["load"] * factor)

    world.add_rule(flow_rule)

    engine.register_world(world)
    return world
