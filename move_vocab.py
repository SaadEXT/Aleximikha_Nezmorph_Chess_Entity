import chess

def build_move_vocab():
    moves = []
    for from_sq in chess.SQUARE_NAMES:
        for to_sq in chess.SQUARE_NAMES:
            moves.append(from_sq + to_sq)
    return {m: i for i, m in enumerate(moves)}

MOVE_VOCAB = build_move_vocab()
VOCAB_SIZE = len(MOVE_VOCAB)

"""
____________________________________________________________________________________________________________________

📄 train/move_vocab.py
Purpose

Defines a shared language between chess and the neural network.

It answers:

“How does the model refer to moves numerically?”

Why this file exists

Neural networks cannot output:

"Nf6+"
"Bxh7+"
"Qg4"

They output indices.

This file defines the mapping:

UCI move ↔ integer index

Why this mapping is centralized

If move mapping is:

Duplicated → bugs
Inconsistent → corrupted learning
Implicit → silent errors

So we define it once, globally.

What it contains

✅ Complete move vocabulary
✅ Deterministic ordering
✅ Vocabulary size

What it must NEVER contain

❌ Probabilities
❌ Chess logic
❌ Legality checks

This file is a dictionary, not a thinker.

Interaction map
train/move_vocab.py
   ↙              ↘
train/train.py   engine/move_selector.py


This file is a shared contract."""