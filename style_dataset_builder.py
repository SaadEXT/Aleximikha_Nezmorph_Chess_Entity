"""
=====================================================================
Aleximikha – Master Style Dataset Builder
---------------------------------------------------------------------

Purpose:
    Curate romantic, aggressive master games into a refined
    training dataset for style fine-tuning.

Targets:
    • Mikhail Tal
    • Alexander Alekhine
    • Rashid Nezhmetdinov
    • Paul Morphy

Features:
    • Multi-PGN ingestion
    • Minimum move filtering
    • Optional decisive-only filtering
    • Sacrifice amplification
    • Position extraction ready for neural training

Philosophy:
    We are not training strength.
    We are training identity.
=====================================================================
"""

import chess
import chess.pgn
import os
from train.dataset import extract_positions


# =========================================================
# CONFIGURATION
# =========================================================

MIN_MOVES = 20
ONLY_DECISIVE = True
AMPLIFY_SACRIFICES = True
SACRIFICE_THRESHOLD = 3  # material imbalance threshold


# =========================================================
# Utility – Detect Material Imbalance
# =========================================================

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}


def material_balance(board):
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def is_sacrificial_position(board):
    return abs(material_balance(board)) >= SACRIFICE_THRESHOLD


# =========================================================
# Game Filter
# =========================================================

def is_valid_game(game):
    """
    Filters out short or irrelevant games.
    """

    if game is None:
        return False

    moves = list(game.mainline_moves())

    if len(moves) < MIN_MOVES:
        return False

    if ONLY_DECISIVE:
        result = game.headers.get("Result", "")
        if result not in ["1-0", "0-1"]:
            return False

    return True


# =========================================================
# Main Dataset Builder
# =========================================================

def build_style_dataset(pgn_paths):
    """
    Returns a list of training positions extracted
    from curated master games.
    """

    dataset = []

    for path in pgn_paths:

        if not os.path.exists(path):
            print(f"⚠ PGN not found: {path}")
            continue

        print(f"📖 Processing: {path}")

        with open(path, encoding="utf-8") as pgn_file:

            while True:
                game = chess.pgn.read_game(pgn_file)

                if game is None:
                    break

                if not is_valid_game(game):
                    continue

                positions = extract_positions(game)

                if AMPLIFY_SACRIFICES:
                    amplified = []
                    board = game.board()

                    for move in game.mainline_moves():
                        board.push(move)

                        if is_sacrificial_position(board):
                            amplified.extend(positions)

                    dataset.extend(positions)
                    dataset.extend(amplified)

                else:
                    dataset.extend(positions)

    print(f"\n🔥 Total style positions collected: {len(dataset)}")
    return dataset
