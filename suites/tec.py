"""
TEC Suite v1
Example suite for TEC orchestration.
"""

def tec_initializer(context):
    context["tec_ready"] = True


def build_tec_suite(engine):
    return engine.create_suite(
        name="tec",
        version="1.0",
        description="TEC orchestration suite.",
        capabilities=["process_orchestration", "pipeline_execution"],
        initializer=tec_initializer
    )
