"""
City Systems Cognitive Domain v1
Example domain for urban systems and flows.
"""

from cognitive.function import CognitiveFunction

def build_city_systems_domain(engine):
    domain = engine.register_domain(
        "city_systems",
        "Cognitive domain for urban flows, infrastructure, and social topology.",
        {"category": "systems"}
    )

    def map_flows(session, payload):
        # payload: {"districts": [...], "edges": [...]} 
        session.set("last_city_model", payload)
        return {"model": "flows_mapped_v1"}

    def stress_test(session, payload):
        # payload: {"scenario": "..."}
        scenario = payload.get("scenario", "baseline")
        return {"scenario": scenario, "result": "stress_test_placeholder_v1"}

    domain.register_function(CognitiveFunction(
        "map_flows",
        "Map flows across city districts.",
        map_flows
    ))

    domain.register_function(CognitiveFunction(
        "stress_test",
        "Run a stress test scenario on the city model.",
        stress_test
    ))

    return domain
