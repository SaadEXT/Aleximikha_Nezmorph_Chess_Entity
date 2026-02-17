"""
=====================================================================
Aleximikha – Neural Hybrid Move Selector (Version 1.5 Stable)
---------------------------------------------------------------------

Design:
    • Neural move ordering
    • Personality shaping (Tal bias preserved)
    • Iterative deepening
    • Alpha-Beta pruning
    • Transposition Table
    • Killer move heuristic
    • Fixed 2-second time control
    • Production stable

Philosophy:
    Artistic aggression + positional sanity.
=====================================================================
"""

import time
import math
import random
import torch
import numpy as np
import chess

from train.move_vocab import MOVE_VOCAB
from engine.concepts import (
    king_safety,
    piece_activity,
    sacrifice_tolerance,
    immediate_material_loss,
)
from engine.evaluation import evaluate_position
from engine.encoder import encode_board


# =========================================================
# CONFIGURATION
# =========================================================

TOP_K = 8
ROOT_TEMPERATURE = 1.1
TREE_TEMPERATURE = 1.0
TIME_LIMIT = 2.0  # Fixed 2 seconds per move
MAX_DEPTH = 6     # Iterative deepening cap

TRANSPOSITION_TABLE = {}
KILLER_MOVES = {}


# =========================================================
# Utility
# =========================================================

def select_move_random(board: chess.Board):
    return random.choice(list(board.legal_moves))


# =========================================================
# Neural Move Ordering
# =========================================================

def neural_order_moves(board, model, ply):

    try:
        device = next(model.parameters()).device
        board_tensor = encode_board(board)

        x = torch.tensor(
            board_tensor,
            dtype=torch.float32,
            device=device
        ).unsqueeze(0)

        with torch.no_grad():
            logits = model(x)[0] / TREE_TEMPERATURE
            probs = torch.softmax(logits, dim=0).cpu().numpy()

        scored = []
        killer = KILLER_MOVES.get(ply)

        for move in board.legal_moves:

            score = 0.0

            uci = move.uci()[:4]
            if uci in MOVE_VOCAB:
                idx = MOVE_VOCAB[uci]
                score += probs[idx] * 10

            if killer and move == killer:
                score += 50

            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                if victim:
                    score += victim.piece_type * 5

            if board.gives_check(move):
                score += 5

            scored.append((move, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored]

    except Exception:
        return list(board.legal_moves)


# =========================================================
# Alpha-Beta with TT + Time Check
# =========================================================

def negamax(board, depth, alpha, beta, model, start_time, ply=0):

    # Time cutoff
    if time.time() - start_time > TIME_LIMIT:
        raise TimeoutError

    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    key = board.fen()
    if key in TRANSPOSITION_TABLE:
        return TRANSPOSITION_TABLE[key]

    best_value = -math.inf
    moves = neural_order_moves(board, model, ply)

    for i, move in enumerate(moves):

        board.push(move)

        reduction = 0
        if depth >= 3 and i >= 4 and not board.is_capture(move):
            reduction = 1

        value = -negamax(
            board,
            depth - 1 - reduction,
            -beta,
            -alpha,
            model,
            start_time,
            ply + 1
        )

        board.pop()

        best_value = max(best_value, value)
        alpha = max(alpha, value)

        if alpha >= beta:
            if not board.is_capture(move):
                KILLER_MOVES[ply] = move
            break

    TRANSPOSITION_TABLE[key] = best_value
    return best_value


# =========================================================
# Root Selection with Iterative Deepening
# =========================================================

def select_move_nn(board_tensor, board: chess.Board, model):

    device = next(model.parameters()).device

    x = torch.tensor(
        board_tensor,
        dtype=torch.float32,
        device=device
    ).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)[0] / ROOT_TEMPERATURE
        probs = torch.softmax(logits, dim=0).cpu().numpy()

    legal_moves = []
    legal_probs = []

    opponent = not board.turn
    danger = king_safety(board, opponent)
    activity = piece_activity(board, board.turn)
    tolerance = sacrifice_tolerance(board, board.turn)

    # Personality shaping
    for move in board.legal_moves:

        uci = move.uci()[:4]
        if uci not in MOVE_VOCAB:
            continue

        idx = MOVE_VOCAB[uci]
        prob = probs[idx]

        if danger > 0.3 and (board.is_capture(move) or board.gives_check(move)):
            prob *= (1.0 + danger)

        if activity < 0.4 and not board.is_capture(move):
            prob *= (1.0 + (0.4 - activity))

        if tolerance > 0.4 and board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker and attacker.piece_type > victim.piece_type:
                prob *= (1.0 + tolerance)

        loss = immediate_material_loss(board, move)
        if loss >= 9:
            continue
        if loss >= 5 and tolerance < 0.6:
            prob *= 0.1

        legal_moves.append(move)
        legal_probs.append(prob)

    if not legal_moves:
        return select_move_random(board)

    legal_probs = np.array(legal_probs)
    legal_probs /= legal_probs.sum()

    move_probs = list(zip(legal_moves, legal_probs))
    move_probs.sort(key=lambda x: x[1], reverse=True)

    candidates = move_probs[:min(TOP_K, len(move_probs))]

    best_move = None
    best_score = -math.inf
    start_time = time.time()

    try:
        for depth in range(1, MAX_DEPTH + 1):

            for move, _ in candidates:

                board.push(move)

                score = -negamax(
                    board,
                    depth - 1,
                    -math.inf,
                    math.inf,
                    model,
                    start_time,
                    ply=1
                )

                board.pop()

                if score > best_score:
                    best_score = score
                    best_move = move

    except TimeoutError:
        pass

    if best_move is None:
        return random.choice(legal_moves)

    return best_move
