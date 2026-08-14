"""
Example Kernel IPC v1
Demonstrates IPC across kernel, runtime, scheduler, sim, tec, governance.
"""

from kernel.ipc.engine import IPCEngine

def build_example_ipc(runtime_engine, scheduler, sim_engine, tec_engine, lawbook_engine):
    ipc = IPCEngine()

    # Channels
    ipc.create_channel("kernel")
    ipc.create_channel("runtime")
    ipc.create_channel("scheduler")
    ipc.create_channel("sim")
    ipc.create_channel("tec")
    ipc.create_channel("governance")

    # Handlers
    ipc.register_handler("kernel", "boot", lambda msg: {"kernel": "booted"})
    ipc.register_handler("runtime", "event", lambda msg: runtime_engine.emit(msg.payload["event"], msg.payload))
    ipc.register_handler("scheduler", "tick", lambda msg: scheduler.run(msg.payload, ticks=1))
    ipc.register_handler("sim", "step", lambda msg: sim_engine.run_model_step(msg.payload["model"], msg.payload["session"], msg.payload))
    ipc.register_handler("tec", "pipeline", lambda msg: tec_engine.run(msg.payload["pipeline"], msg.payload, msg.metadata))
    ipc.register_handler("governance", "check", lambda msg: lawbook_engine.check_invariants(msg.payload))

    # Send messages
    ipc.send("kernel", "boot", {})
    ipc.send("runtime", "event", {"event": "routing_init"})
    ipc.send("scheduler", "tick", {"kernel_ready": True})
    ipc.send("sim", "step", {"model": "chess_model", "session": "sess_chess_1"})
    ipc.send("tec", "pipeline", {"pipeline": "cognitive_transform_pipeline"}, {"session": "sess_tec_1"})
    ipc.send("governance", "check", {"substrate_active": True})

    # Dispatch all channels
    results = {
        "kernel": ipc.dispatch("kernel"),
        "runtime": ipc.dispatch("runtime"),
        "scheduler": ipc.dispatch("scheduler"),
        "sim": ipc.dispatch("sim"),
        "tec": ipc.dispatch("tec"),
        "governance": ipc.dispatch("governance")
    }

    return ipc, results
