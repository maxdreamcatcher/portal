"""
Music Space Model v1
Example SIM.MODE model for emotional music geometry.
"""

from sim.model import SimModel

def build_music_space_model(engine):
    def step_fn(state, context, input_payload):
        track_id = input_payload.get("track_id", "unknown")
        state["last_track"] = track_id
        # Placeholder geometry
        geometry = {
            "warmth": 0.7,
            "distance": 0.3,
            "tension": 0.5
        }
        return {
            "state": state,
            "geometry": geometry
        }

    model = SimModel(
        "music_space_model",
        "Model for emotional geometry of tracks.",
        {"category": "music"},
        step_fn=step_fn
    )

    model.initialize({})
    engine.register_model(model)
    return model
