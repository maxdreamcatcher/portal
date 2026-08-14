"""
Umbrella Invariants v1
Defines the core invariants enforced by the Portal‑OS kernel.
"""

INVARIANTS = {
    "identity_integrity": "Identity physics must remain consistent.",
    "governance_safety": "Umbrella governance rules must not be violated.",
    "routing_consistency": "Routing topology must remain stable.",
    "substrate_alignment": "Class‑C substrate must remain aligned."
}


def check_invariant(name):
    return INVARIANTS.get(name, None)
