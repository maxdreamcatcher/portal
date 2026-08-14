"""
SIM.MODE Engine v1
Registry + runner for models and worlds.
"""

from sim.model import SimModel
from sim.world import SimWorld
from sim.session import SimSession

class SimEngine:
    def __init__(self):
        self.models = {}
        self.worlds = {}
        self.sessions = {}

    # Models
    def register_model(self, model: SimModel):
        self.models[model.name] = model

    def get_model(self, name):
        return self.models.get(name)

    # Worlds
    def register_world(self, world: SimWorld):
        self.worlds[world.name] = world

    def get_world(self, name):
        return self.worlds.get(name)

    # Sessions
    def create_session(self, session_id, model_name=None, world_name=None, metadata=None):
        session = SimSession(session_id, model_name, world_name, metadata)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    # Execution
    def run_model_step(self, model_name, session_id, input_payload=None):
        model = self.get_model(model_name)
        if not model:
            return {"error": "model_not_found"}

        session = self.get_session(session_id)
        if not session:
            return {"error": "session_not_found"}

        result = model.step(session, input_payload)
        session.record({
            "type": "model_step",
            "model": model_name,
            "input": input_payload,
            "result": result
        })
        return result

    def run_world_tick(self, world_name, session_id, context=None):
        world = self.get_world(world_name)
        if not world:
            return {"error": "world_not_found"}

        session = self.get_session(session_id)
        if not session:
            return {"error": "session_not_found"}

        ctx = context or {}
        world.apply_rules(ctx)
        session.record({
            "type": "world_tick",
            "world": world_name,
            "context": ctx,
            "entities": world.entities
        })
        return {
            "world": world_name,
            "entities": world.entities
        }

    def describe(self):
        return {
            "models": {name: m.describe() for name, m in self.models.items()},
            "worlds": {name: w.describe() for name, w in self.worlds.items()},
            "sessions": {sid: s.describe() for sid, s in self.sessions.items()}
        }
