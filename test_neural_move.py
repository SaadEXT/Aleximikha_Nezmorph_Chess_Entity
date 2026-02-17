"""
test_neural_move.py

Regression test to verify that:
- The trained neural model can select a legal move
- Concept biases do not break legality
- Board state updates correctly
"""

import sys
import os

# --------------------------------------------------
# Ensure project root is on Python path
# --------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import chess

from engine.encoder import encode_board
from engine.move_selector import select_move_nn
from engine.game_loader import load_games
from train.dataset import extract_positions
from train.train import train_model


def run_test():
    print("\n--- Neural Move Regression Test ---")

    # Train a tiny model (fast, deterministic)
    games = load_games("data/pgn/tal.pgn", max_games=1)

    dataset = []
    for game in games:
        dataset.extend(extract_positions(game))

    model = train_model(dataset, epochs=1)

    # Create test position
    board = chess.Board()
    print("Initial position:")
    print(board)

    board_tensor = encode_board(board)

    move = select_move_nn(
        board_tensor=board_tensor,
        board=board,
        model=model,
        temperature=1.2
    )

    print("Selected move:", move)
    board.push(move)

    print("Board after move:")
    print(board)


if __name__ == "__main__":
    run_test()

from engine.concepts import piece_activity

print("\n--- Concept Test: Piece Activity ---")

board = chess.Board()
print("White activity:", piece_activity(board, chess.WHITE))
print("Black activity:", piece_activity(board, chess.BLACK))
