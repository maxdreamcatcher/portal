"""
Chess Cognitive Domain v1
Example cognitive domain for chess strategy.
"""

from cognitive.function import CognitiveFunction

def build_chess_domain(engine):
    domain = engine.register_domain(
        "chess",
        "Cognitive domain for chess strategy and evaluation.",
        {"category": "games"}
    )

    def eval_position(session, payload):
        # payload: {"fen": "..."}
        fen = payload.get("fen", "")
        session.set("last_fen", fen)
        # Placeholder: real eval would plug into SIM.MODE or external engine
        return {"fen": fen, "evaluation": "uncalibrated_v1"}

    def suggest_move(session, payload):
        # payload: {"fen": "..."}
        fen = payload.get("fen", "")
        session.set("last_fen", fen)
        return {"fen": fen, "suggested_move": "Nf3 (placeholder_v1)"}

    domain.register_function(CognitiveFunction(
        "eval_position",
        "Evaluate a chess position.",
        eval_position
    ))

    domain.register_function(CognitiveFunction(
        "suggest_move",
        "Suggest a move for a given position.",
        suggest_move
    ))

    return domain
