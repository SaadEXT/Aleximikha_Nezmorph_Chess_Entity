"""
analysis.py

Analysis Mode for the chess engine.

Responsibilities:
- Accept a chess.Board position
- Ask the engine to suggest a move
- Explain the decision using human-readable concepts

This module does NOT:
- Train the model
- Play full games
- Modify engine state

It is a pure interpretation layer.
"""

import chess

from engine.encoder import encode_board
from engine.move_selector import select_move_nn
from engine.concepts import (
    king_safety,
    piece_activity,
    sacrifice_tolerance,
)


def analyze_position(board: chess.Board, model):
    """
    Analyzes a position and returns:
    - suggested_move (chess.Move)
    - explanation (list of strings)
    """

    explanation = []

    # -----------------------------------
    # 1. Ask the engine for a move
    # -----------------------------------
    board_tensor = encode_board(board)
    move = select_move_nn(
        board_tensor=board_tensor,
        board=board,
        model=model,
        temperature=1.1,
    )

    # -----------------------------------
    # 2. Evaluate human concepts
    # -----------------------------------
    opponent = not board.turn

    king_danger = king_safety(board, opponent)
    activity = piece_activity(board, board.turn)
    tolerance = sacrifice_tolerance(board, board.turn)

    # -----------------------------------
    # 3. Generate explanations
    # -----------------------------------

    if king_danger > 0.6:
        explanation.append(
            "The opponent king is exposed, so attacking chances are important."
        )
    elif king_danger > 0.3:
        explanation.append(
            "There is some pressure on the opponent king."
        )
    else:
        explanation.append(
            "The opponent king appears reasonably safe."
        )

    if activity < 0.3:
        explanation.append(
            "Your pieces are not very active, so improving piece activity is a priority."
        )
    elif activity > 0.6:
        explanation.append(
            "Your pieces are very active and well-coordinated."
        )

    if tolerance > 0.6:
        explanation.append(
            "Material sacrifices may be justified due to initiative and pressure."
        )
    elif tolerance < 0.3:
        explanation.append(
            "Material safety is important in this position."
        )

    explanation.append(
        f"The move {move.uci()} aligns with these positional considerations."
    )

    return move, explanation
