"""
=====================================================================
Aleximikha – Canonical Evaluation & Search Engine (Endgame Enhanced)
---------------------------------------------------------------------

Philosophy:
    Static truth + Tactical verification + Aggressive pressure.

Design:
    • Modular evaluation
    • Attack-map dominance (Tal-mode)
    • Phase scaling
    • Endgame intelligence layer
    • Quiescence search
    • Negamax + Alpha-Beta
    • Principal Variation Search (PVS)
    • Late Move Reductions (LMR)
    • Killer Move heuristic
    • History heuristic
    • Transposition Table

No feature removals.
Only evolution.
=====================================================================
"""

import chess
import math
from collections import defaultdict

from engine.endgame import (
    detect_endgame_phase,
    king_activity_bonus,
    passed_pawn_bonus,
    opposition_bonus,
)

# =========================================================
# CONSTANTS
# =========================================================

PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.25,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0,
}

CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]

BISHOP_PAIR_BONUS = 0.35
TEMPO_BONUS = 0.15

PASSED_PAWN_BONUS = 0.4
ISOLATED_PAWN_PENALTY = 0.2
DOUBLED_PAWN_PENALTY = 0.15

ROOK_OPEN_FILE_BONUS = 0.35
ROOK_SEMI_OPEN_FILE_BONUS = 0.18

ATTACK_WEIGHT = 0.015
KING_ATTACK_WEIGHT = 0.05

# =========================================================
# TRANSPOSITION TABLE
# =========================================================

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2

TRANSPOSITION_TABLE = {}

# =========================================================
# KILLER + HISTORY HEURISTICS
# =========================================================

KILLER_MOVES = defaultdict(lambda: [None, None])
HISTORY_HEURISTIC = defaultdict(int)

# =========================================================
# GAME PHASE
# =========================================================

def game_phase(board):
    total = 0
    for piece_type, value in PIECE_VALUES.items():
        if piece_type == chess.KING:
            continue
        total += (
            len(board.pieces(piece_type, chess.WHITE)) +
            len(board.pieces(piece_type, chess.BLACK))
        ) * value
    return min(1.0, total / 62.0)


# =========================================================
# STATIC EVALUATION
# =========================================================

def evaluate_material(board):
    score = 0.0
    for pt, val in PIECE_VALUES.items():
        score += len(board.pieces(pt, chess.WHITE)) * val
        score -= len(board.pieces(pt, chess.BLACK)) * val
    return score


def evaluate_bishop_pair(board):
    score = 0.0
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += BISHOP_PAIR_BONUS
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= BISHOP_PAIR_BONUS
    return score


def evaluate_pawn_structure(board):
    score = 0.0

    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        pawn_files = {}

        for sq in pawns:
            f = chess.square_file(sq)
            pawn_files.setdefault(f, []).append(sq)

        for f, squares in pawn_files.items():

            # Doubled pawns
            if len(squares) > 1:
                penalty = DOUBLED_PAWN_PENALTY * (len(squares) - 1)
                score -= penalty if color == chess.WHITE else -penalty

            for sq in squares:
                rank = chess.square_rank(sq)

                # Isolated
                if all(adj not in pawn_files for adj in [f-1, f+1]):
                    score -= ISOLATED_PAWN_PENALTY if color == chess.WHITE else -ISOLATED_PAWN_PENALTY

                # Passed
                is_passed = True
                for adj in [f-1, f, f+1]:
                    if 0 <= adj <= 7:
                        for enemy in board.pieces(chess.PAWN, not color):
                            if chess.square_file(enemy) == adj:
                                enemy_rank = chess.square_rank(enemy)
                                if color == chess.WHITE and enemy_rank > rank:
                                    is_passed = False
                                if color == chess.BLACK and enemy_rank < rank:
                                    is_passed = False
                if is_passed:
                    advance = rank/7 if color == chess.WHITE else (7-rank)/7
                    bonus = PASSED_PAWN_BONUS * advance
                    score += bonus if color == chess.WHITE else -bonus

    return score


def evaluate_center_control(board):
    score = 0.0
    for sq in CENTER_SQUARES:
        score += 0.1 * (
            len(board.attackers(chess.WHITE, sq)) -
            len(board.attackers(chess.BLACK, sq))
        )
    return score


def evaluate_rook_activity(board):
    score = 0.0
    for color in [chess.WHITE, chess.BLACK]:
        for rook_sq in board.pieces(chess.ROOK, color):
            file = chess.square_file(rook_sq)

            friendly = any(chess.square_file(p)==file for p in board.pieces(chess.PAWN, color))
            enemy = any(chess.square_file(p)==file for p in board.pieces(chess.PAWN, not color))

            if not friendly and not enemy:
                score += ROOK_OPEN_FILE_BONUS if color==chess.WHITE else -ROOK_OPEN_FILE_BONUS
            elif not friendly and enemy:
                score += ROOK_SEMI_OPEN_FILE_BONUS if color==chess.WHITE else -ROOK_SEMI_OPEN_FILE_BONUS

    return score


def evaluate_attack_pressure(board):
    score = 0.0

    for sq in chess.SQUARES:
        score += ATTACK_WEIGHT * (
            len(board.attackers(chess.WHITE, sq)) -
            len(board.attackers(chess.BLACK, sq))
        )

    for color in [chess.WHITE, chess.BLACK]:
        king_sq = board.king(color)
        if king_sq:
            attackers = len(board.attackers(not color, king_sq))
            score += KING_ATTACK_WEIGHT * attackers if color==chess.BLACK else -KING_ATTACK_WEIGHT * attackers

    return score


# =========================================================
# ENDGAME INTELLIGENCE LAYER
# =========================================================

def evaluate_endgame_layer(board):
    phase = detect_endgame_phase(board)

    if phase not in ["endgame", "pure_pawn"]:
        return 0.0

    score = 0.0

    # King activity becomes important
    score += king_activity_bonus(board, chess.WHITE) * 0.25
    score -= king_activity_bonus(board, chess.BLACK) * 0.25

    # Passed pawns more critical in endgame
    score += passed_pawn_bonus(board, chess.WHITE) * 0.4
    score -= passed_pawn_bonus(board, chess.BLACK) * 0.4

    # Opposition logic
    score += opposition_bonus(board, chess.WHITE) * 0.3

    return score


# =========================================================
# MAIN EVALUATION
# =========================================================

def evaluate_position(board):

    if board.is_checkmate():
        return -9999
    if board.is_stalemate():
        return 0

    score = 0.0

    score += evaluate_material(board)
    score += evaluate_bishop_pair(board)
    score += evaluate_pawn_structure(board)
    score += evaluate_center_control(board)
    score += evaluate_rook_activity(board)
    score += evaluate_attack_pressure(board)
    score += evaluate_endgame_layer(board)

    score += TEMPO_BONUS if board.turn == chess.WHITE else -TEMPO_BONUS

    return score


# =========================================================
# MOVE ORDERING
# =========================================================

def order_moves(board, depth):
    moves = list(board.legal_moves)

    def move_score(move):
        score = 0

        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            if victim:
                score += PIECE_VALUES[victim.piece_type] * 10

        if board.gives_check(move):
            score += 5

        if move in KILLER_MOVES[depth]:
            score += 8

        score += HISTORY_HEURISTIC[move]

        return score

    moves.sort(key=move_score, reverse=True)
    return moves


# =========================================================
# QUIESCENCE
# =========================================================

def quiescence(board, alpha, beta):
    stand_pat = evaluate_position(board)

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if not board.is_capture(move):
            continue

        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# =========================================================
# NEGAMAX + PVS + LMR + TT
# =========================================================

def search(board, depth, alpha, beta):

    if depth == 0:
        return quiescence(board, alpha, beta)

    key = (board.fen(), depth)
    if key in TRANSPOSITION_TABLE:
        entry = TRANSPOSITION_TABLE[key]
        if entry["depth"] >= depth:
            return entry["score"]

    best_value = -math.inf
    first_move = True

    for i, move in enumerate(order_moves(board, depth)):

        board.push(move)

        reduction = 0
        if depth >= 3 and i >= 3 and not board.is_capture(move):
            reduction = 1

        if first_move:
            score = -search(board, depth-1, -beta, -alpha)
            first_move = False
        else:
            score = -search(board, depth-1-reduction, -alpha-1, -alpha)
            if alpha < score < beta:
                score = -search(board, depth-1, -beta, -alpha)

        board.pop()

        if score > best_value:
            best_value = score

        if score > alpha:
            alpha = score

        if alpha >= beta:
            if not board.is_capture(move):
                KILLER_MOVES[depth][1] = KILLER_MOVES[depth][0]
                KILLER_MOVES[depth][0] = move
                HISTORY_HEURISTIC[move] += depth * depth
            break

    TRANSPOSITION_TABLE[key] = {
        "depth": depth,
        "score": best_value
    }

    return best_value
