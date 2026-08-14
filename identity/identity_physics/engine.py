"""
Identity Physics Engine v1
Evaluates identity objects against physics rules and Umbrella constraints.
"""

from identity.identity_physics.model import IdentityPhysicsModel
from identity.identity_physics.rules import (
    rule_identity_has_core,
    rule_identity_has_cognitive,
    rule_identity_has_domain,
    rule_roles_are_valid,
    rule_identifier_is_valid
)


def constraint_identity_integrity(identity):
    return (
        rule_identifier_is_valid(identity)
        and rule_roles_are_valid(identity)
        and rule_identity_has_core(identity)
    )


def constraint_cognitive_alignment(identity):
    return "cognitive" in identity.layers and isinstance(identity.layers["cognitive"], dict)


def build_identity_physics_engine():
    engine = IdentityPhysicsModel()

    # Add rules
    engine.add_rule(rule_identity_has_core)
    engine.add_rule(rule_identity_has_cognitive)
    engine.add_rule(rule_identity_has_domain)
    engine.add_rule(rule_roles_are_valid)
    engine.add_rule(rule_identifier_is_valid)

    # Add constraints
    engine.add_constraint(constraint_identity_integrity)
    engine.add_constraint(constraint_cognitive_alignment)

    return engine
