"""
Music Emotion Cognitive Domain v1
Example domain for emotional geometry of songs.
"""

from cognitive.function import CognitiveFunction

def build_music_emotion_domain(engine):
    domain = engine.register_domain(
        "music_emotion",
        "Cognitive domain for emotional geometry of music.",
        {"category": "music"}
    )

    def analyze_track(session, payload):
        # payload: {"track_id": "...", "features": {...}}
        track_id = payload.get("track_id", "unknown")
        session.set("last_track", track_id)
        return {
            "track_id": track_id,
            "geometry": "placeholder_v1",
            "axes": ["warmth", "distance", "tension"]
        }

    def compare_tracks(session, payload):
        # payload: {"tracks": [id1, id2, ...]}
        tracks = payload.get("tracks", [])
        return {
            "tracks": tracks,
            "relationship": "placeholder_v1"
        }

    domain.register_function(CognitiveFunction(
        "analyze_track",
        "Analyze emotional geometry of a track.",
        analyze_track
    ))

    domain.register_function(CognitiveFunction(
        "compare_tracks",
        "Compare emotional geometry across tracks.",
        compare_tracks
    ))

    return domain
