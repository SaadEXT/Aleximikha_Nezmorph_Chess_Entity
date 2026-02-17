"""
=====================================================================
Aleximikha – Legendary Dataset Builder
---------------------------------------------------------------------

Purpose:
    Build weighted neural dataset from legendary grandmaster games.

Legends Included:
    - Mikhail Tal
    - Paul Morphy
    - Alexander Alekhine
    - Garry Kasparov
    - Judit Polgar

Philosophy:
    Train on all games.
    Reward brilliance.
    Learn from defeat.
    Weight victories higher.

Output:
    training_dataset.pt
=====================================================================
"""

import os
import torch
import chess
import chess.pgn
import numpy as np

from engine.encoder import encode_board
from train.move_vocab import MOVE_VOCAB


# =========================================================
# CONFIGURATION
# =========================================================

PGN_FOLDER = "data/pgn"
OUTPUT_FILE = "training_dataset.pt"

WIN_WEIGHT = 1.5
DRAW_WEIGHT = 1.0
LOSS_WEIGHT = 0.7

MIN_GAME_LENGTH = 10  # filter out trivial games


# =========================================================
# Utility: Determine Result Weight
# =========================================================

def get_game_weight(game, player_color):

    result = game.headers.get("Result", "")

    if result == "1-0":
        return WIN_WEIGHT if player_color == chess.WHITE else LOSS_WEIGHT

    elif result == "0-1":
        return WIN_WEIGHT if player_color == chess.BLACK else LOSS_WEIGHT

    elif result == "1/2-1/2":
        return DRAW_WEIGHT

    return DRAW_WEIGHT


# =========================================================
# Main Dataset Builder
# =========================================================

def build_dataset():

    inputs = []
    targets = []
    weights = []

    total_positions = 0

    for filename in os.listdir(PGN_FOLDER):

        if not filename.endswith(".pgn"):
            continue

        path = os.path.join(PGN_FOLDER, filename)
        print(f"Processing {filename}...")

        with open(path, encoding="utf-8", errors="ignore") as pgn_file:

            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break

                board = game.board()
                moves = list(game.mainline_moves())

                if len(moves) < MIN_GAME_LENGTH:
                    continue

                # Detect which legend side we're training
                white_name = game.headers.get("White", "")
                black_name = game.headers.get("Black", "")

                for move in moves:

                    board_tensor = encode_board(board)

                    uci = move.uci()[:4]

                    if uci in MOVE_VOCAB:

                        move_index = MOVE_VOCAB[uci]

                        # Determine which player played move
                        player_color = board.turn

                        game_weight = get_game_weight(game, player_color)

                        inputs.append(board_tensor)
                        targets.append(move_index)
                        weights.append(game_weight)

                        total_positions += 1

                    board.push(move)

    print(f"\nTotal positions collected: {total_positions}")

    dataset = {
        "inputs": torch.tensor(np.array(inputs), dtype=torch.float32),
        "targets": torch.tensor(targets, dtype=torch.long),
        "weights": torch.tensor(weights, dtype=torch.float32),
    }

    torch.save(dataset, OUTPUT_FILE)

    print(f"\nDataset saved to {OUTPUT_FILE}")


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":
    build_dataset()
