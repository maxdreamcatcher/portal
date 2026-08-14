"""
Clock Driver v1
Provides system time.
"""

import time

def clock_initializer(context):
    context["clock_ready"] = True

def build_clock_driver(engine):
    return engine.create_driver(
        name="clock",
        version="1.0",
        description="Provides system time.",
        provides=["system_time"],
        initializer=clock_initializer
    )
