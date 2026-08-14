"""
Example Process Manager v1
Demonstrates process creation, execution, waiting, stopping, killing.
"""

from process.manager import ProcessManager

def build_example_process_manager(runtime_engine, sim_engine, tec_engine, cognitive_engine):
    pm = ProcessManager()

    # Process: runtime event
    p_runtime = pm.spawn(
        "runtime",
        lambda proc, payload: runtime_engine.emit(payload["event"], payload)
    )

    # Process: SIM.MODE step
    p_sim = pm.spawn(
        "sim",
        lambda proc, payload: sim_engine.run_model_step(
            payload["model"], payload["session"], payload
        )
    )

    # Process: TEC pipeline
    p_tec = pm.spawn(
        "tec",
        lambda proc, payload: tec_engine.run(
            payload["pipeline"], payload, payload.get("metadata", {})
        )
    )

    # Process: cognitive function
    p_cog = pm.spawn(
        "cognitive",
        lambda proc, payload: cognitive_engine.run(
            payload["domain"], payload["function"], payload["session"], payload.get("payload", {})
        )
    )

    # Run processes
    r1 = pm.run(p_runtime.pid, {"event": "routing_init"})
    r2 = pm.run(p_sim.pid, {"model": "chess_model", "session": "sess_chess_1"})
    r3 = pm.run(p_tec.pid, {"pipeline": "cognitive_transform_pipeline"})
    r4 = pm.run(p_cog.pid, {"domain": "chess", "function": "eval_position", "session": "sess_chess_1", "payload": {"fen": "startpos"}})

    # Stop + kill
    pm.stop(p_sim.pid)
    pm.kill(p_runtime.pid)

    return pm, [r1, r2, r3, r4], pm.describe()
