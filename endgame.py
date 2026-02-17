"""
=====================================================================
Aleximikha – Endgame Intelligence Layer v1
---------------------------------------------------------------------

Purpose:
    Lightweight endgame awareness without tablebases.

Features:
    • Phase detection
    • King activity bonus
    • Passed pawn prioritization
    • Opposition detection
    • Simplified material heuristics

No external dependencies.
No tablebase downloads.
=====================================================================
"""

import chess


# =========================================================
# PHASE DETECTION
# =========================================================

def detect_endgame_phase(board: chess.Board):
    """
    Returns:
        "opening", "middlegame", "endgame", or "pure_pawn"
    """

    non_pawn_material = 0
    piece_count = 0
    queens = 0

    for piece in board.piece_map().values():
        piece_count += 1
        if piece.piece_type == chess.QUEEN:
            queens += 1
        if piece.piece_type != chess.PAWN and piece.piece_type != chess.KING:
            non_pawn_material += piece.piece_type

    if piece_count <= 4:
        return "pure_pawn"

    if queens == 0 and non_pawn_material < 10:
        return "endgame"

    if non_pawn_material < 20:
        return "endgame"

    return "middlegame"


# =========================================================
# KING ACTIVITY
# =========================================================

def king_activity_bonus(board: chess.Board, color):
    """
    Encourages king centralization in endgames.
    """

    king_square = board.king(color)
    if king_square is None:
        return 0

    file = chess.square_file(king_square)
    rank = chess.square_rank(king_square)

    # Distance from center
    center_distance = abs(file - 3.5) + abs(rank - 3.5)

    return max(0, 4 - center_distance)


# =========================================================
# PASSED PAWN BONUS
# =========================================================

def passed_pawn_bonus(board: chess.Board, color):
    """
    Rewards passed pawns.
    """

    bonus = 0

    for square, piece in board.piece_map().items():
        if piece.color != color or piece.piece_type != chess.PAWN:
            continue

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        is_passed = True

        for offset in [-1, 0, 1]:
            check_file = file + offset
            if 0 <= check_file <= 7:
                for r in range(8):
                    sq = chess.square(check_file, r)
                    enemy = board.piece_at(sq)
                    if enemy and enemy.piece_type == chess.PAWN and enemy.color != color:
                        if (color == chess.WHITE and r > rank) or \
                           (color == chess.BLACK and r < rank):
                            is_passed = False

        if is_passed:
            advance = rank if color == chess.WHITE else (7 - rank)
            bonus += advance * 0.5

    return bonus


# =========================================================
# OPPOSITION DETECTION
# =========================================================

def opposition_bonus(board: chess.Board, color):
    """
    Basic opposition detection for king vs king scenarios.
    """

    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)

    if white_king is None or black_king is None:
        return 0

    wf = chess.square_file(white_king)
    wr = chess.square_rank(white_king)

    bf = chess.square_file(black_king)
    br = chess.square_rank(black_king)

    if abs(wf - bf) == 2 and wr == br:
        return 1 if color == chess.WHITE else -1

    if abs(wr - br) == 2 and wf == bf:
        return 1 if color == chess.WHITE else -1

    return 0
