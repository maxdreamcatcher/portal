"""
Suite Registry v1
Stores and manages all Portal‑OS suites.
"""

class SuiteRegistry:
    def __init__(self):
        self.suites = {}

    def register(self, suite: "Suite"):
        self.suites[suite.manifest.name] = suite

    def load(self, name, context):
        suite = self.suites.get(name)
        if not suite:
            return {"error": "suite_not_found"}
        return suite.load(context)

    def describe(self):
        return {name: suite.describe() for name, suite in self.suites.items()}
