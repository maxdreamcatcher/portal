"""
Umbrella Lawbook Engine v1
Coordinates rule evaluation, invariant checking, and escalation.
"""

from umbrella.lawbook.lawbook import UmbrellaLawbook, LawViolation
from umbrella.lawbook.rules import (
    rule_identity_integrity,
    rule_governance_safety,
    rule_routing_consistency,
    rule_substrate_alignment
)
from umbrella.lawbook.invariants import (
    invariant_identity_must_exist,
    invariant_kernel_must_be_booted,
    invariant_sim_mode_must_be_loaded
)
from umbrella.lawbook.escalation import (
    handle_low_severity,
    handle_medium_severity,
    handle_high_severity
)


def build_lawbook_engine():
    lawbook = UmbrellaLawbook()

    # Add rules
    lawbook.add_rule("identity_integrity", "Identity must remain stable.", rule_identity_integrity)
    lawbook.add_rule("governance_safety", "Governance must remain safe.", rule_governance_safety)
    lawbook.add_rule("routing_consistency", "Routing must remain consistent.", rule_routing_consistency)
    lawbook.add_rule("substrate_alignment", "Substrate must remain aligned.", rule_substrate_alignment)

    # Add invariants
    lawbook.add_invariant("identity_exists", "Identity must exist.", invariant_identity_must_exist)
    lawbook.add_invariant("kernel_booted", "Kernel must be booted.", invariant_kernel_must_be_booted)
    lawbook.add_invariant("sim_mode_loaded", "SIM.MODE must be loaded.", invariant_sim_mode_must_be_loaded)

    # Add escalation paths
    lawbook.add_escalation_path("low", handle_low_severity)
    lawbook.add_escalation_path("medium", handle_medium_severity)
    lawbook.add_escalation_path("high", handle_high_severity)

    return lawbook
