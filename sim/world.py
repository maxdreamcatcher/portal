"""
SIM.MODE World v1
Defines a named world with entities and rules.
"""

class SimWorld:
    def __init__(self, name, description="", metadata=None):
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.entities = {}
        self.rules = []

    def add_entity(self, id_, data):
        self.entities[id_] = data

    def add_rule(self, rule_fn):
        self.rules.append(rule_fn)

    def apply_rules(self, context):
        for rule in self.rules:
            rule(self.entities, context)

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "entities": self.entities,
            "rules_count": len(self.rules)
        }
