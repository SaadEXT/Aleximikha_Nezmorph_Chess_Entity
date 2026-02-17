"""
Test 4 — Romantic Opening Book
--------------------------------
"""

import chess
from train.romantic_book import get_book_move


def main():
    board = chess.Board()

    move = get_book_move(board)

    print("Book move:", move)
    print("Is legal?", move in board.legal_moves if move else None)


if __name__ == "__main__":
    main()
