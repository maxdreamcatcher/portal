"""
SIM.MODE Engine v1
Coordinates Core, Cognitive, and Domain layers.

Engine responsibilities:
- Manage cognitive layers
- Evaluate cognitive functions
- Evaluate domain modules
- Provide unified SIM.MODE interface
"""

from sim.mode.core import CoreLayer, CognitiveState
from sim.mode.cognitive import CognitiveLayer, CognitiveFunction
from sim.mode.domain import DomainLayer, DomainModule

class SimModeEngine:
    def __init__(self):
        self.core = CoreLayer()
        self.cognitive = CognitiveLayer()
        self.domain = DomainLayer()

    def add_core_state(self, name, data=None):
        state = CognitiveState(name, data)
        self.core.add_state(state)
        return state

    def add_cognitive_function(self, name, fn):
        cognitive_fn = CognitiveFunction(name, fn)
        self.cognitive.add_function(cognitive_fn)
        return cognitive_fn

    def add_domain_module(self, name, evaluator):
        module = DomainModule(name, evaluator)
        self.domain.add_module(module)
        return module

    def run_cognitive(self, name, context):
        return self.cognitive.run(name, context)

    def run_domain(self, name, context):
        return self.domain.evaluate(name, context)

    def describe(self):
        return {
            "core": self.core.describe(),
            "cognitive": self.cognitive.describe(),
            "domain": self.domain.describe()
        }
