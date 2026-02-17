"""
=====================================================================
Aleximikha – Romantic Opening Book Loader
---------------------------------------------------------------------

Loads and queries the prebuilt romantic opening book.

Used during early moves to inject stylistic openings
from Tal, Morphy, Alekhine, Polgar, Kasparov dataset.

Safe fallback if book not found.
=====================================================================
"""

import os
import json
import random
import chess

# Path where build_romantic_book saved the book
BOOK_PATH = "romantic_opening_book.json"

_opening_book = None


def load_book():
    global _opening_book

    if _opening_book is not None:
        return

    if not os.path.exists(BOOK_PATH):
        print("⚠ Romantic opening book not found.")
        _opening_book = {}
        return

    with open(BOOK_PATH, "r") as f:
        _opening_book = json.load(f)


def get_book_move(board: chess.Board):
    """
    Returns a book move if available for current position.
    Otherwise returns None.
    """

    load_book()

    if not _opening_book:
        return None

    fen_key = board.board_fen()

    if fen_key not in _opening_book:
        return None

    moves = _opening_book[fen_key]

    if not moves:
        return None

    move_uci = random.choice(moves)

    try:
        return chess.Move.from_uci(move_uci)
    except:
        return None
