"""
=====================================================================
Aleximikha – Romantic Opening Book Builder
---------------------------------------------------------------------

Purpose:
    Build deterministic aggressive opening book from legend PGNs.

Scoring Bias:
    • Wins preferred
    • Short decisive games preferred
    • Early checks & captures rewarded
    • Draw-heavy lines penalized

Output:
    romantic_opening_book.json
=====================================================================
"""

import chess
import chess.pgn
import os
import json
from collections import defaultdict

# CONFIG
PGN_FOLDER = "data/pgn"
MAX_PLIES = 14
OUTPUT_FILE = "romantic_opening_book.json"

# Romantic scoring weights
WIN_BONUS = 5
SHORT_GAME_BONUS = 3
CHECK_BONUS = 1
CAPTURE_BONUS = 1
DRAW_PENALTY = -3


def process_pgn(file_path, book_data):

    with open(file_path, encoding="utf-8", errors="ignore") as pgn_file:

        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break

            result = game.headers.get("Result", "*")

            board = game.board()

            ply_count = 0

            for move in game.mainline_moves():

                if ply_count >= MAX_PLIES:
                    break

                fen = board.fen()
                board.push(move)

                score = 0

                if result == "1-0" or result == "0-1":
                    score += WIN_BONUS

                if game.end().ply() < 40:
                    score += SHORT_GAME_BONUS

                if board.is_check():
                    score += CHECK_BONUS

                if board.is_capture(move):
                    score += CAPTURE_BONUS

                if result == "1/2-1/2":
                    score += DRAW_PENALTY

                book_data[fen][move.uci()] += score

                ply_count += 1


def build_opening_book():

    book_data = defaultdict(lambda: defaultdict(int))

    for filename in os.listdir(PGN_FOLDER):
        if filename.lower().endswith(".pgn"):
            print(f"Processing {filename}...")
            process_pgn(os.path.join(PGN_FOLDER, filename), book_data)

    final_book = {}

    for fen, moves in book_data.items():
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        final_book[fen] = best_move

    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_book, f)

    print(f"\nRomantic Opening Book saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_opening_book()
