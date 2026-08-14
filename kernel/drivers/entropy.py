"""
Entropy Driver v1
Provides random entropy.
"""

import os

def entropy_initializer(context):
    context["entropy_ready"] = True

def build_entropy_driver(engine):
    return engine.create_driver(
        name="entropy",
        version="1.0",
        description="Provides random entropy.",
        provides=["entropy"],
        initializer=entropy_initializer
    )
