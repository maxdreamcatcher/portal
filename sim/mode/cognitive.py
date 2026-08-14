"""
SIM.MODE Cognitive Layer v1
Defines cognitive processing primitives used by SIM and Identity Physics.

Cognitive responsibilities:
- Cognitive functions
- Layered reasoning
- Deterministic evaluation
"""

class CognitiveFunction:
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self, context):
        return self.fn(context)


class CognitiveLayer:
    def __init__(self):
        self.functions = {}

    def add_function(self, cognitive_fn: CognitiveFunction):
        self.functions[cognitive_fn.name] = cognitive_fn

    def run(self, name, context):
        fn = self.functions.get(name)
        if fn:
            return fn.run(context)
        return None

    def describe(self):
        return list(self.functions.keys())
