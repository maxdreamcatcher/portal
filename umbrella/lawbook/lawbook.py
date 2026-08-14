"""
Umbrella Lawbook v1
Portal‑OS v4

Defines the governance rules, invariants, and escalation pathways
that govern all Portal‑OS subsystems.

Lawbook responsibilities:
- Define rules
- Define invariants
- Define violations
- Define escalation paths
"""

class LawRule:
    def __init__(self, name, description, evaluator):
        self.name = name
        self.description = description
        self.evaluator = evaluator

    def evaluate(self, context):
        return self.evaluator(context)


class LawInvariant:
    def __init__(self, name, description, evaluator):
        self.name = name
        self.description = description
        self.evaluator = evaluator

    def check(self, context):
        return self.evaluator(context)


class LawViolation:
    def __init__(self, rule_name, context, severity):
        self.rule_name = rule_name
        self.context = context
        self.severity = severity

    def describe(self):
        return {
            "rule": self.rule_name,
            "context": self.context,
            "severity": self.severity
        }


class UmbrellaLawbook:
    def __init__(self):
        self.rules = {}
        self.invariants = {}
        self.escalation_paths = {}

    def add_rule(self, name, description, evaluator):
        self.rules[name] = LawRule(name, description, evaluator)

    def add_invariant(self, name, description, evaluator):
        self.invariants[name] = LawInvariant(name, description, evaluator)

    def add_escalation_path(self, name, handler):
        self.escalation_paths[name] = handler

    def evaluate_rules(self, context):
        results = {"passed": [], "failed": []}
        for name, rule in self.rules.items():
            if rule.evaluate(context):
                results["passed"].append(name)
            else:
                results["failed"].append(name)
        return results

    def check_invariants(self, context):
        results = {"passed": [], "failed": []}
        for name, invariant in self.invariants.items():
            if invariant.check(context):
                results["passed"].append(name)
            else:
                results["failed"].append(name)
        return results

    def escalate(self, violation: LawViolation):
        handler = self.escalation_paths.get(violation.severity)
        if handler:
            return handler(violation)
        return {"status": "no_escalation_path"}
