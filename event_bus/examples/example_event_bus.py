"""
Example Event Bus v1
Demonstrates broadcast events across kernel, runtime, sim, tec, governance, suites.
"""

from event_bus.bus import EventBus

def build_example_event_bus(runtime_engine, sim_engine, tec_engine, lawbook_engine, suite_engine):
    bus = EventBus()

    # Channels
    bus.create_channel("kernel")
    bus.create_channel("runtime")
    bus.create_channel("sim")
    bus.create_channel("tec")
    bus.create_channel("governance")
    bus.create_channel("suites")

    # Subscriptions
    bus.subscribe("kernel", "kernel_logger", lambda evt: {"logged": evt.describe()})
    bus.subscribe("runtime", "runtime_executor", lambda evt: runtime_engine.emit(evt.type, evt.payload))
    bus.subscribe("sim", "sim_runner", lambda evt: sim_engine.run_model_step(evt.payload["model"], evt.payload["session"], evt.payload))
    bus.subscribe("tec", "pipeline_runner", lambda evt: tec_engine.run(evt.payload["pipeline"], evt.payload, evt.metadata))
    bus.subscribe("governance", "gov_checker", lambda evt: lawbook_engine.check_invariants(evt.payload))
    bus.subscribe("suites", "suite_executor", lambda evt: suite_engine.run(evt.payload["suite"], evt.payload["module"], evt.payload.get("payload", {}), evt.metadata))

    # Publish events
    results = {
        "kernel": bus.publish("kernel", "boot", {}),
        "runtime": bus.publish("runtime", "routing_init", {"event": "routing_init"}),
        "sim": bus.publish("sim", "step", {"model": "chess_model", "session": "sess_chess_1"}),
        "tec": bus.publish("tec", "pipeline", {"pipeline": "cognitive_transform_pipeline"}, {"session": "sess_tec_1"}),
        "governance": bus.publish("governance", "check", {"substrate_active": True}),
        "suites": bus.publish("suites", "run", {"suite": "chess", "module": "eval_position", "payload": {"fen": "startpos"}}, {"session": "sess_chess_1"})
    }

    return bus, results
