"""
Example TEC Pipeline v1
Demonstrates how TEC pipelines are constructed.
"""

from tec.orchestration.engine import TECOrchestrationEngine
from tec.processes.example_process import example_process

def build_example_pipeline():
    engine = TECOrchestrationEngine()

    # Register process
    engine.add_process("example", example_process)

    # Create pipeline
    pipeline = engine.add_pipeline("example_pipeline")

    # Attach process
    engine.attach_process_to_pipeline("example_pipeline", "example")

    return engine
