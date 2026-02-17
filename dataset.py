import chess
from engine.encoder import encode_board

def extract_positions(game):
    board = game.board()
    samples = []

    for move in game.mainline_moves():
        state = encode_board(board)
        samples.append((state, move.uci()))
        board.push(move)

    return samples

"""
____________________________________________________________________________________________________________________

📄 train/dataset.py

Purpose

This file defines how we extract learning samples from human games.

It answers:

“What does one learning example look like?”

Why this file exists

Human games are sequential and messy.

Neural networks need:

Clean
Repeated
Uniform samples

This file performs that transformation.

What it does

✅ Iterates through a chess game
✅ Captures board state before a move
✅ Pairs it with the human’s chosen move

Result:

(position_tensor) → (human move)


That’s the core of imitation learning.

What it deliberately ignores

❌ Who won
❌ Engine evaluations
❌ Material count
❌ “Best move” concepts

We are learning choice, not correctness.

Interaction map
engine/game_loader.py
        ↓
train/dataset.py
        ↓
engine/encoder.py


This file sits exactly between raw games and learning.

Design philosophy (important)

We do NOT skip “bad” human moves.

Why?

Humans are inconsistent
Style emerges from imperfection
Over-cleaning kills personality

This file preserves human texture."""