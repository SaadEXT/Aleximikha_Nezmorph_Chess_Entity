"""
=====================================================================
Aleximikha – Romantic Puzzle Miner
---------------------------------------------------------------------

Purpose:
    Automatically extract tactical puzzles from training dataset.

Features:
    • Tactical swing detection
    • Engine-verified best move
    • Theme classification
    • Difficulty estimation
    • JSON export for training_mode

Output:
    data/puzzles/romantic_mined.json
=====================================================================
"""

import torch
import chess
import json
import os

from engine.evaluation import search, evaluate_position

DATASET_PATH = "training_dataset.pt"
OUTPUT_PATH = "data/puzzles/romantic_mined.json"

MIN_SWING = 2.0
SEARCH_DEPTH = 4
MAX_PUZZLES = 500


# =========================================================
# THEME CLASSIFICATION
# =========================================================

def classify_theme(board, move):

    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)

        if victim and attacker:
            if attacker.piece_type > victim.piece_type:
                return "sacrifice"
            return "tactic"

    if board.gives_check(move):
        return "check_attack"

    return "positional"


# =========================================================
# PUZZLE MINER
# =========================================================

def mine_puzzles():

    print("Loading dataset...")
    data = torch.load(DATASET_PATH)

    puzzles = []

    for idx, (board_tensor, _) in enumerate(data):

        if len(puzzles) >= MAX_PUZZLES:
            break

        board = reconstruct_board_from_tensor(board_tensor)

        if board.is_game_over():
            continue

        base_eval = evaluate_position(board)

        best_move = None
        best_score = -9999

        for move in board.legal_moves:
            board.push(move)
            score = -search(board, SEARCH_DEPTH - 1, -9999, 9999)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        swing = best_score - base_eval

        if swing >= MIN_SWING:

            theme = classify_theme(board, best_move)

            puzzles.append({
                "fen": board.fen(),
                "solution": best_move.uci(),
                "theme": theme,
                "difficulty": round(min(5, swing), 2)
            })

            print(f"Puzzle {len(puzzles)} found. Theme: {theme}")

    os.makedirs("data/puzzles", exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(puzzles, f, indent=2)

    print("\nMining complete.")
    print(f"{len(puzzles)} puzzles saved to {OUTPUT_PATH}")


# =========================================================
# BOARD RECONSTRUCTION (Placeholder)
# =========================================================

def reconstruct_board_from_tensor(board_tensor):
    """
    You must implement this using your encoder logic.
    For now, return starting board placeholder.
    """
    return chess.Board()


if __name__ == "__main__":
    mine_puzzles()
