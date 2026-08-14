"""
Umbrella Lawbook Invariants v1
Defines invariants that must never be violated.
"""

def invariant_identity_must_exist(context):
    return "identity" in context and context["identity"] is not None


def invariant_kernel_must_be_booted(context):
    return context.get("kernel_booted", False)


def invariant_sim_mode_must_be_loaded(context):
    return context.get("sim_mode_loaded", False)
