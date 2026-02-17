"""
=====================================================================
Aleximikha Tutor Mode – Romantic Genius Mentor (Ultimate Edition)
---------------------------------------------------------------------

Purpose:
    Post-game analysis with artistic, instructive commentary
    validated by depth-4 engine calculation.

Philosophy:
    Not punishment.
    Not sterile engine scores.
    But revelation.

Features:
    • Full evaluate_position()
    • Depth-4 negamax search()
    • Best-move comparison
    • Evaluation swing detection
    • Tactical oversight detection
    • Strength/weakness profiling
    • Romantic narrative commentary

Tone:
    Tal guiding you through fire.
=====================================================================
"""

import chess
import chess.pgn
import io
import math

from engine.evaluation import evaluate_position, search


# =========================================================
# CONFIGURATION
# =========================================================

BLUNDER_THRESHOLD = 2.5
MISTAKE_THRESHOLD = 1.0
INACCURACY_THRESHOLD = 0.5

ANALYSIS_DEPTH = 4  # Increased depth for real validation


# =========================================================
# Core Game Analyzer
# =========================================================

def analyze_game(pgn_string):
    """
    Entry point for Tutor Mode.
    Returns a structured romantic analysis report.
    """

    game = chess.pgn.read_game(io.StringIO(pgn_string))
    board = game.board()

    report = []
    move_number = 1

    for move in game.mainline_moves():

        position_before = board.copy()

        # Evaluate before move
        eval_before = evaluate_position(position_before)

        # Compute best engine move at this position
        best_move, best_score = find_best_move(position_before)

        # Play actual move
        board.push(move)
        eval_after = evaluate_position(board)

        swing = eval_after - eval_before
        best_vs_played_diff = best_score - eval_after

        commentary = classify_and_comment(
            move,
            swing,
            best_vs_played_diff,
            best_move
        )

        report.append({
            "move_number": move_number,
            "move": move.uci(),
            "best_move": best_move.uci() if best_move else None,
            "evaluation_swing": round(swing, 2),
            "missed_value": round(best_vs_played_diff, 2),
            "commentary": commentary
        })

        if board.turn == chess.WHITE:
            move_number += 1

    summary = generate_summary(report)

    return {
        "move_analysis": report,
        "summary": summary
    }


# =========================================================
# Engine Best Move Finder
# =========================================================

def find_best_move(board):
    """
    Uses depth-4 negamax search to determine best move
    from current position.
    """

    best_value = -math.inf
    best_move = None

    for move in board.legal_moves:
        board.push(move)
        value = -search(board, ANALYSIS_DEPTH - 1, -math.inf, math.inf)
        board.pop()

        if value > best_value:
            best_value = value
            best_move = move

    return best_move, best_value


# =========================================================
# Classification Logic
# =========================================================

def classify_and_comment(move, swing, missed_value, best_move):
    """
    Determines move quality based on:
        • Evaluation swing
        • Missed engine opportunity
    """

    abs_swing = abs(swing)

    # Tactical oversight (missed win)
    if missed_value >= BLUNDER_THRESHOLD:
        return romantic_missed_win(move, best_move)

    if abs_swing >= BLUNDER_THRESHOLD:
        return romantic_blunder(move)

    elif abs_swing >= MISTAKE_THRESHOLD:
        return romantic_mistake(move)

    elif abs_swing >= INACCURACY_THRESHOLD:
        return romantic_inaccuracy(move)

    else:
        return romantic_praise(move)


# =========================================================
# Romantic Commentary Layer
# =========================================================

def romantic_blunder(move):
    return (
        f"{move.uci()}… a tragic lunge into the abyss. "
        "The position demanded patience — calculation — restraint. "
        "Even brilliance must bow to precision."
    )


def romantic_mistake(move):
    return (
        f"{move.uci()} burns with intention, yet something sharper was waiting. "
        "The board whispered a stronger continuation."
    )


def romantic_inaccuracy(move):
    return (
        f"{move.uci()} is serviceable, but not sublime. "
        "There was a path of greater harmony."
    )


def romantic_praise(move):
    return (
        f"{move.uci()} — elegant and purposeful. "
        "A move aligned with the soul of the position."
    )


def romantic_missed_win(move, best_move):
    return (
        f"{move.uci()} carried fire — yet destiny was closer. "
        f"The move {best_move.uci()} would have ignited something decisive. "
        "In such moments, calculation must be fearless."
    )


# =========================================================
# Summary Generator
# =========================================================

def generate_summary(report):
    """
    Produces structured coaching feedback.
    """

    blunders = sum(1 for r in report if abs(r["evaluation_swing"]) >= BLUNDER_THRESHOLD)
    mistakes = sum(1 for r in report if MISTAKE_THRESHOLD <= abs(r["evaluation_swing"]) < BLUNDER_THRESHOLD)
    missed_wins = sum(1 for r in report if r["missed_value"] >= BLUNDER_THRESHOLD)

    if blunders == 0 and mistakes == 0 and missed_wins == 0:
        return (
            "This was a performance of clarity and conviction. "
            "Your intuition walked hand in hand with calculation."
        )

    if missed_wins >= 2:
        return (
            "Opportunities were within reach — decisive blows hovered near. "
            "Sharpen calculation in critical moments."
        )

    if blunders >= 3:
        return (
            "The battle was rich with lessons. "
            "Tactical discipline must grow stronger."
        )

    if mistakes >= 2:
        return (
            "You navigated well, but the turning points demanded deeper vision."
        )

    return (
        "A spirited encounter. With refinement in calculation, "
        "your play will ascend."
    )
