"""
SIM.MODE Core Layer v1
Defines the foundational cognitive primitives used by SIM and Portal‑OS.

Core responsibilities:
- Represent cognitive states
- Maintain stable identity physics anchors
- Provide deterministic transitions
"""

class CognitiveState:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}

    def update(self, key, value):
        self.data[key] = value

    def describe(self):
        return {
            "state": self.name,
            "data": self.data
        }


class CoreLayer:
    def __init__(self):
        self.states = {}

    def add_state(self, state: CognitiveState):
        self.states[state.name] = state

    def get_state(self, name):
        return self.states.get(name)

    def describe(self):
        return {name: state.describe() for name, state in self.states.items()}
