"""
encoder.py

Responsible for converting a chess.Board into a neural-friendly tensor.
This representation is deliberately simple and extendable.

Current format:
- 12 x 8 x 8 tensor
- 6 planes for white pieces
- 6 planes for black pieces

This file contains NO chess logic.
It only answers: "What does the board look like numerically?"
"""


import numpy as np
import chess

PIECE_MAP = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

def encode_board(board: chess.Board):
    """
    Converts a chess.Board into a 12x8x8 tensor.

    Why this exists:
    Neural networks cannot reason about chess.Board objects.
    This function strips away meaning and keeps structure only.

    This is the foundation for all learning.
    """
    
    """
    Returns a (12, 8, 8) tensor:
    6 planes for white pieces
    6 planes for black pieces
    """
    tensor = np.zeros((12, 8, 8), dtype=np.float32)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            offset = 0 if piece.color == chess.WHITE else 6
            idx = PIECE_MAP[piece.piece_type] + offset
            tensor[idx][row][col] = 1.0

    return tensor


"""
_______________________________________________________________________________________________________________________

📄 engine/encoder.py
Purpose

This is one of the most critical files in the entire project.

It converts:

A symbolic chess position
into
A numerical representation the brain can learn from

Why this file exists

Neural networks cannot:

Read chess notation

Understand objects

Interpret symbols

They only understand numbers and structure.

This file is the translator.

What this file is responsible for

✅ Board → tensor
✅ Stable, deterministic encoding
✅ Extendable representation

What it must NEVER do

❌ Decide moves
❌ Evaluate positions
❌ Contain learning logic

Encoding must be neutral, not opinionated.

Why our encoding is simple (by design)

We use:

12 x 8 x 8 tensor


Why?

Transparent

Debuggable

Easy to extend

Industry-proven

Clever encodings come later — if needed.

Interaction map
chess.Board
      ↓
encoder.encode_board()
      ↓
train/dataset.py
      ↓
engine/model.py


This file is the bridge between chess and learning."""