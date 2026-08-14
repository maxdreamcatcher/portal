"""
Identity Physics Model v1
Portal‑OS v4

Defines the core identity physics model used across SIM, Identity, and Umbrella layers.
Identity physics governs:
- Identity structure
- Cognitive layers
- Role binding
- Stability rules
- Mutation constraints
"""

class Identity:
    def __init__(self, identifier, roles=None, layers=None):
        self.identifier = identifier
        self.roles = roles or []
        self.layers = layers or {
            "core": {},
            "cognitive": {},
            "domain": {}
        }

    def add_role(self, role):
        self.roles.append(role)

    def set_layer(self, layer_name, data):
        self.layers[layer_name] = data

    def describe(self):
        return {
            "id": self.identifier,
            "roles": self.roles,
            "layers": self.layers
        }


class IdentityPhysicsModel:
    def __init__(self):
        self.rules = []
        self.constraints = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def evaluate(self, identity):
        results = {
            "rules_passed": [],
            "rules_failed": [],
            "constraints_passed": [],
            "constraints_failed": []
        }

        for rule in self.rules:
            if rule(identity):
                results["rules_passed"].append(rule.__name__)
            else:
                results["rules_failed"].append(rule.__name__)

        for constraint in self.constraints:
            if constraint(identity):
                results["constraints_passed"].append(constraint.__name__)
            else:
                results["constraints_failed"].append(constraint.__name__)

        return results
