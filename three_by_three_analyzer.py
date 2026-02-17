"""
=====================================================================
Aleximikha – 3×3 Decisive Moment Analyzer
---------------------------------------------------------------------

Purpose:
    Post-game conversational deep coaching.

Method:
    • Identify top 3 largest evaluation swings (absolute)
    • Identify 1 strongest positive swing (brilliancy)
    • Dynamically search better continuation
    • Explain in human language
    • Provide short principal variation

Philosophy:
    Not chess.com engine spam.
    Not cold numeric review.

    Storytelling.
    Clarity.
    Retention.

This module integrates:
    • evaluate_position
    • search
    • dynamic depth scaling
=====================================================================
"""

import chess
import math
import chess.pgn


from engine.evaluation import evaluate_position, search


# =========================================================
# CONFIG
# =========================================================

BASE_DEPTH = 3
MAX_DEPTH = 5
MIN_DEPTH = 2


# =========================================================
# Dynamic Depth Logic
# =========================================================

def dynamic_depth(board: chess.Board):
    """
    Adjust search depth based on phase and complexity.
    """

    material_count = len(board.piece_map())

    if material_count <= 8:
        return MAX_DEPTH  # Endgame → deeper

    if board.is_check():
        return MAX_DEPTH  # Tactical moment

    if material_count <= 14:
        return BASE_DEPTH + 1

    return BASE_DEPTH


# =========================================================
# Best Move Finder
# =========================================================

def find_best_move(board: chess.Board, depth):

    best_value = -math.inf
    best_move = None

    for move in board.legal_moves:
        board.push(move)
        value = -search(board, depth - 1, -math.inf, math.inf)
        board.pop()

        if value > best_value:
            best_value = value
            best_move = move

    return best_move, best_value


# =========================================================
# Evaluation Swing Analysis
# =========================================================

def collect_swing_data(game: chess.pgn.Game):

    board = game.board()
    swings = []

    for move in game.mainline_moves():

        board_before = board.copy(stack=False)

        before = evaluate_position(board)
        board.push(move)
        after = evaluate_position(board)

        swing = after - before

        swings.append({
            "move": move,
            "board_before": board_before,
            "swing": swing
        })

    return swings


# =========================================================
# Human Explanation Generator
# =========================================================

def explain_difference(board_before, player_move, best_move):

    explanation = []

    explanation.append(f"You played {player_move.uci()}.")

    # Evaluate player move
    board = board_before.copy()
    board.push(player_move)
    eval_player = evaluate_position(board)

    # Evaluate best move
    board = board_before.copy()
    board.push(best_move)
    eval_best = evaluate_position(board)

    delta = round(eval_best - eval_player, 2)

    explanation.append(
        f"The engine preferred {best_move.uci()}, which improves the position by approximately {delta}."
    )

    # Short PV
    board = board_before.copy()
    board.push(best_move)

    depth = min(dynamic_depth(board_before), 4)

    pv_line = [best_move.uci()]

    for _ in range(2):
        reply, _ = find_best_move(board, depth - 1)
        if reply is None:
            break
        pv_line.append(reply.uci())
        board.push(reply)

    explanation.append("A short continuation could be: " + " ".join(pv_line))

    explanation.append(
        "The key idea is improving coordination, increasing pressure, and avoiding unnecessary structural weaknesses."
    )

    return "\n".join(explanation)


# =========================================================
# Main 3×3 Analyzer
# =========================================================

def analyze_game_3x3(game: chess.pgn.Game):

    swings = collect_swing_data(game)

    # Sort by absolute swing
    sorted_swings = sorted(
        swings,
        key=lambda x: abs(x["swing"]),
        reverse=True
    )

    decisive_moments = sorted_swings[:3]

    # Best positive swing
    positive_swings = sorted(
        swings,
        key=lambda x: x["swing"],
        reverse=True
    )

    brilliant_moment = positive_swings[0] if positive_swings else None

    results = []

    # --- Negative / decisive moments ---
    for moment in decisive_moments:

        board_before = moment["board_before"]
        player_move = moment["move"]

        depth = dynamic_depth(board_before)
        best_move, _ = find_best_move(board_before, depth)

        explanation = explain_difference(
            board_before,
            player_move,
            best_move
        )

        results.append({
            "type": "decisive",
            "swing": round(moment["swing"], 2),
            "explanation": explanation
        })

    # --- Brilliant move ---
    if brilliant_moment:

        board_before = brilliant_moment["board_before"]
        player_move = brilliant_moment["move"]

        results.append({
            "type": "brilliant",
            "swing": round(brilliant_moment["swing"], 2),
            "explanation":
                f"Brilliant moment: {player_move.uci()} improved your position significantly. "
                "This move created dynamic pressure and shifted the balance in your favor."
        })

    return results

# =========================================================
# Wrapper Class Interface (for Coach + Tests)
# =========================================================

class ThreeByThreeAnalyzer:
    """
    Public wrapper for 3×3 post-game analysis.

    Usage:
        analyzer = ThreeByThreeAnalyzer()
        report = analyzer.analyze_game(pgn_string)
    """

    def __init__(self):
        pass

    def analyze_game(self, pgn_string: str):
        import chess.pgn
        from io import StringIO

        game = chess.pgn.read_game(StringIO(pgn_string))
        results = analyze_game_3x3(game)

        # Structured return format
        return {
            "critical_moments": [
                r for r in results if r["type"] == "decisive"
            ],
            "brilliant_move": next(
                (r for r in results if r["type"] == "brilliant"),
                None
            )
        }

