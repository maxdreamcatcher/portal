"""
Umbrella Lawbook Rules v1
Defines governance rules for Portal‑OS.
"""

def rule_identity_integrity(context):
    return context.get("identity_integrity", True)


def rule_governance_safety(context):
    return context.get("governance_safety", True)


def rule_routing_consistency(context):
    return context.get("routing_consistency", True)


def rule_substrate_alignment(context):
    return context.get("substrate_alignment", True)
