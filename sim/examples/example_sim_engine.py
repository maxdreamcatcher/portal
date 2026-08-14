"""
Example SIM.MODE Engine v1
Demonstrates models, worlds, and sessions.
"""

from sim.engine import SimEngine
from sim.examples.city_world import build_city_world
from sim.examples.chess_model import build_chess_model
from sim.examples.music_space_model import build_music_space_model

def build_example_sim_engine():
    engine = SimEngine()

    # Register models and worlds
    build_city_world(engine)
    build_chess_model(engine)
    build_music_space_model(engine)

    # Create sessions
    sess_city = engine.create_session("sess_city_1", world_name="city_world")
    sess_chess = engine.create_session("sess_chess_1", model_name="chess_model")
    sess_music = engine.create_session("sess_music_1", model_name="music_space_model")

    # Run world tick
    r_city = engine.run_world_tick("city_world", sess_city.id, {"flow_factor": 0.9})

    # Run model steps
    r_chess = engine.run_model_step("chess_model", sess_chess.id, {"fen": "startpos"})
    r_music = engine.run_model_step("music_space_model", sess_music.id, {"track_id": "track_001"})

    return engine, [r_city, r_chess, r_music]
