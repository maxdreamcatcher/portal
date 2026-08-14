"""
I/O Driver v1
Provides basic input/output operations.
"""

def io_initializer(context):
    context["io_ready"] = True

def build_io_driver(engine):
    return engine.create_driver(
        name="io",
        version="1.0",
        description="Provides basic I/O operations.",
        provides=["read", "write"],
        initializer=io_initializer
    )
