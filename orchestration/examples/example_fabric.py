"""
Example Orchestration Fabric v1
Demonstrates orchestration across kernel, runtime, TEC, SIM, and suites.
"""

from orchestration.engine import OrchEngine

def build_example_fabric():
    engine = OrchEngine()
    fabric = engine.fabric

    # Nodes
    fabric.add_node("kernel_boot", lambda ctx: {"kernel": "booted"})
    fabric.add_node("runtime_start", lambda ctx: {"runtime": "started"})
    fabric.add_node("tec_pipeline", lambda ctx: {"tec": "pipeline_executed"})
    fabric.add_node("sim_chamber", lambda ctx: {"sim": "chamber_active"})
    fabric.add_node("suite_load", lambda ctx: {"suites": "loaded"})

    # Links (conditional orchestration)
    fabric.add_link(
        "kernel_boot",
        "runtime_start",
        condition=lambda ctx, res: res["result"].get("kernel") == "booted"
    )
    fabric.add_link(
        "runtime_start",
        "tec_pipeline",
        condition=lambda ctx, res: res["result"].get("runtime") == "started"
    )
    fabric.add_link(
        "tec_pipeline",
        "sim_chamber",
        condition=lambda ctx, res: True
    )
    fabric.add_link(
        "sim_chamber",
        "suite_load",
        condition=lambda ctx, res: True
    )

    # Flow
    flow = fabric.add_flow("portal-os-orchestration")
    flow.add_step("kernel_boot")

    # Context
    context = {"env": "dev"}

    # Run
    result = engine.run_flow("portal-os-orchestration", context)

    return engine, result
