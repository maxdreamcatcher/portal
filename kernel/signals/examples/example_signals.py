"""
Example Kernel Signals v1
Demonstrates interrupts across kernel, runtime, substrate, sim, tec, governance.
"""

from kernel.signals.engine import SignalEngine

def build_example_signals(runtime_engine, substrate_engine, sim_engine, tec_engine, lawbook_engine):
    se = SignalEngine()

    # Handlers
    se.register_handler(
        "kernel_fault",
        "Handle kernel faults.",
        lambda sig: {"kernel_recovery": True, "payload": sig.payload}
    )

    se.register_handler(
        "runtime_trap",
        "Trap runtime errors.",
        lambda sig: runtime_engine.emit("runtime_trap", sig.payload)
    )

    se.register_handler(
        "substrate_drop",
        "Handle substrate instability.",
        lambda sig: substrate_engine.activate_layer(sig.payload["layer"])
    )

    se.register_handler(
        "sim_overload",
        "Handle SIM.MODE overload.",
        lambda sig: sim_engine.run_world_tick(sig.payload["world"], sig.payload["session"], {"flow_factor": 0.5})
    )

    se.register_handler(
        "tec_abort",
        "Abort TEC pipeline.",
        lambda sig: {"aborted_pipeline": sig.payload["pipeline"]}
    )

    se.register_handler(
        "governance_violation",
        "Escalate Umbrella violations.",
        lambda sig: lawbook_engine.escalate(sig.payload)
    )

    # Raise signals
    results = {
        "kernel_fault": se.raise_signal("kernel_fault", "high", {"error": "panic"}),
        "runtime_trap": se.raise_signal("runtime_trap", "medium", {"event": "bad_state"}),
        "substrate_drop": se.raise_signal("substrate_drop", "high", {"layer": "planetary"}),
        "sim_overload": se.raise_signal("sim_overload", "high", {"world": "city_world", "session": "sess_city_1"}),
        "tec_abort": se.raise_signal("tec_abort", "critical", {"pipeline": "cognitive_transform_pipeline"}),
        "governance_violation": se.raise_signal("governance_violation", "critical", {"rule": "substrate_active"})
    }

    return se, results
