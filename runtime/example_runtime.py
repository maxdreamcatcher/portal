"""
Example Portal‑OS Runtime v1
Demonstrates runtime initialization and event handling.
"""

from runtime.engine import RuntimeEngine

def build_example_runtime():
    rt = RuntimeEngine()

    # Initialize + start
    rt.initialize()
    rt.start()

    # Register handlers
    rt.register_handler("kernel_boot", lambda evt: {"kernel": "booted"})
    rt.register_handler("routing_init", lambda evt: {"routing": "initialized"})
    rt.register_handler("substrate_load", lambda evt: {"substrate": "loaded"})
    rt.register_handler("umbrella_check", lambda evt: {"umbrella": "validated"})
    rt.register_handler("suite_load", lambda evt: {"suites": "loaded"})

    # Emit events
    rt.emit("kernel_boot")
    rt.emit("routing_init")
    rt.emit("substrate_load")
    rt.emit("umbrella_check")
    rt.emit("suite_load")

    # Run runtime loop
    results = rt.run(ticks=5)
    return rt, results
