"""
=====================================================================
Aleximikha – Motif Detection Engine v1
---------------------------------------------------------------------

Purpose:
    Detect tactical and endgame motifs in a position.

Used by:
    • Romantic puzzle miner
    • Tutor profiling system
    • Future training analytics

Design:
    Pure board-based analysis.
    No neural dependence.
=====================================================================
"""

import chess


# =========================================================
# PUBLIC ENTRY
# =========================================================

def detect_motifs(board: chess.Board):
    """
    Returns list of detected motifs in the current position.
    """

    motifs = []

    motifs += detect_forks(board)
    motifs += detect_pins(board)
    motifs += detect_skewers(board)
    motifs += detect_discovered_attacks(board)
    motifs += detect_hanging_pieces(board)
    motifs += detect_opposition(board)

    return list(set(motifs))


# =========================================================
# FORKS
# =========================================================

def detect_forks(board):
    motifs = []

    for move in board.legal_moves:
        board.push(move)

        attackers = board.attackers(board.turn, move.to_square)
        attacked_pieces = []

        for square in board.attacks(move.to_square):
            piece = board.piece_at(square)
            if piece and piece.color != board.turn:
                attacked_pieces.append(piece)

        if len(attacked_pieces) >= 2:
            motifs.append("fork")

        board.pop()

    return motifs


# =========================================================
# PINS
# =========================================================

def detect_pins(board):
    motifs = []

    for square, piece in board.piece_map().items():
        if board.is_pinned(piece.color, square):
            motifs.append("pin")

    return motifs


# =========================================================
# SKEWERS
# =========================================================

def detect_skewers(board):
    motifs = []

    for square, piece in board.piece_map().items():
        if piece.piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN]:

            for target in board.attacks(square):
                target_piece = board.piece_at(target)

                if target_piece and target_piece.color != piece.color:

                    board.push(chess.Move(square, target))
                    behind = board.attacks(target)

                    for sq2 in behind:
                        piece2 = board.piece_at(sq2)
                        if piece2 and piece2.color != piece.color:
                            if piece2.piece_type > target_piece.piece_type:
                                motifs.append("skewer")

                    board.pop()

    return motifs


# =========================================================
# DISCOVERED ATTACKS
# =========================================================

def detect_discovered_attacks(board):
    motifs = []

    for move in board.legal_moves:
        board.push(move)

        if board.is_check():
            board.pop()
            continue

        attackers = board.attackers(board.turn, board.king(not board.turn))
        if attackers:
            motifs.append("discovered_attack")

        board.pop()

    return motifs


# =========================================================
# HANGING PIECES
# =========================================================

def detect_hanging_pieces(board):
    motifs = []

    for square, piece in board.piece_map().items():
        if board.is_attacked_by(not piece.color, square):
            if not board.is_attacked_by(piece.color, square):
                motifs.append("hanging_piece")

    return motifs


# =========================================================
# OPPOSITION
# =========================================================

def detect_opposition(board):
    motifs = []

    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    if wk is None or bk is None:
        return motifs

    wf = chess.square_file(wk)
    wr = chess.square_rank(wk)
    bf = chess.square_file(bk)
    br = chess.square_rank(bk)

    if abs(wf - bf) == 2 and wr == br:
        motifs.append("opposition")

    if abs(wr - br) == 2 and wf == bf:
        motifs.append("opposition")

    return motifs
