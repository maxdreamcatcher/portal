"""
Governance Dashboard v1
Provides a simple UI abstraction for governance status.
"""

class GovernanceDashboard:
    def __init__(self, lawbook_engine):
        self.lawbook = lawbook_engine

    def snapshot(self, context=None):
        context = context or {}
        return {
            "rules": self.lawbook.evaluate_rules(context),
            "invariants": self.lawbook.check_invariants(context),
            "lawbook": self.lawbook.describe()
        }
