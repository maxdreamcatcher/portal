"""
Example Cognitive Engine v1
Demonstrates domains, functions, and sessions.
"""

from cognitive.engine import CognitiveEngine
from cognitive.examples.chess_domain import build_chess_domain
from cognitive.examples.city_systems_domain import build_city_systems_domain
from cognitive.examples.music_emotion_domain import build_music_emotion_domain

def build_example_cognitive_engine():
    engine = CognitiveEngine()

    # Register domains
    build_chess_domain(engine)
    build_city_systems_domain(engine)
    build_music_emotion_domain(engine)

    # Create sessions
    chess_session = engine.create_session("chess", "sess_chess_1")
    city_session = engine.create_session("city_systems", "sess_city_1")
    music_session = engine.create_session("music_emotion", "sess_music_1")

    # Run some cognitive functions
    r1 = engine.run("chess", "eval_position", chess_session.id, {"fen": "startpos"})
    r2 = engine.run("city_systems", "map_flows", city_session.id, {"districts": [], "edges": []})
    r3 = engine.run("music_emotion", "analyze_track", music_session.id, {"track_id": "track_001"})

    return engine, [r1, r2, r3]
