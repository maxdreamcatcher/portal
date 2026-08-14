"""
Identity Physics Rules v1
Defines the rule set governing identity stability and integrity.
"""

def rule_identity_has_core(identity):
    return "core" in identity.layers and isinstance(identity.layers["core"], dict)


def rule_identity_has_cognitive(identity):
    return "cognitive" in identity.layers and isinstance(identity.layers["cognitive"], dict)


def rule_identity_has_domain(identity):
    return "domain" in identity.layers and isinstance(identity.layers["domain"], dict)


def rule_roles_are_valid(identity):
    return isinstance(identity.roles, list)


def rule_identifier_is_valid(identity):
    return isinstance(identity.identifier, str) and len(identity.identifier) > 0
