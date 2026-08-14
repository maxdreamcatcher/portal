"""
SIM.MODE Domain Layer v1
Defines domain-specific cognitive modules used by Portal‑OS suites.

Domain responsibilities:
- Domain cognition
- Domain context evaluation
- Domain-specific reasoning
"""

class DomainModule:
    def __init__(self, name, evaluator):
        self.name = name
        self.evaluator = evaluator

    def evaluate(self, context):
        return self.evaluator(context)


class DomainLayer:
    def __init__(self):
        self.modules = {}

    def add_module(self, module: DomainModule):
        self.modules[module.name] = module

    def evaluate(self, name, context):
        module = self.modules.get(name)
        if module:
            return module.evaluate(context)
        return None

    def describe(self):
        return list(self.modules.keys())
