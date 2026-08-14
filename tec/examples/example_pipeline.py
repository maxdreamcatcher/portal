"""
Example TEC Pipeline v1
Cognition → Transform → Evaluate → Output
"""

from tec.engine import TECEngine
from tec.pipeline import TECPipeline
from tec.stage import TECStage

def build_example_tec_pipeline():
    engine = TECEngine()

    pipeline = TECPipeline(
        "cognitive_transform_pipeline",
        "Example pipeline that processes cognitive payloads."
    )

    # Stage 1: Cognition
    pipeline.add_stage(TECStage(
        "cognition",
        "Initial cognitive interpretation.",
        lambda ctx, payload: {"interpreted": payload}
    ))

    # Stage 2: Transform
    pipeline.add_stage(TECStage(
        "transform",
        "Transform interpreted payload.",
        lambda ctx, payload: {"transformed": payload}
    ))

    # Stage 3: Evaluate
    pipeline.add_stage(TECStage(
        "evaluate",
        "Evaluate transformed payload.",
        lambda ctx, payload: {"evaluation": "placeholder_v1", "input": payload}
    ))

    # Stage 4: Output
    pipeline.add_stage(TECStage(
        "output",
        "Produce final output.",
        lambda ctx, payload: {"final_output": payload}
    ))

    engine.register_pipeline(pipeline)

    # Run pipeline
    result = engine.run(
        "cognitive_transform_pipeline",
        {"input": "hello_world"},
        metadata={"session": "tec_example_1"}
    )

    return engine, result
