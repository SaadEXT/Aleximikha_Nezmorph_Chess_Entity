"""
concepts.py

This module extracts high-level chess concepts from a board position.
These concepts are numeric signals that represent human chess ideas,
not engine evaluations.

Examples of concepts:
- King safety
- Piece activity
- Attacked squares
- Central presence

These signals are used to bias move selection,
NOT to replace the neural network.

The neural model predicts preferences.
This module injects personality.
"""
import chess

def king_safety(board: chess.Board, color: chess.Color) -> float:
    """
    Returns a value between 0.0 and 1.0 indicating how unsafe the given color's king is.
    Higher = more danger.
    """

    king_square = board.king(color)
    if king_square is None:
        # King missing should never happen, but be safe
        return 1.0

    danger = 0.0

    # 1. King in the center is dangerous
    rank = chess.square_rank(king_square)
    file = chess.square_file(king_square)
    if 2 <= rank <= 5 and 2 <= file <= 5:
        danger += 0.3

    # 2. Count enemy attacks near the king
    for square in chess.SQUARES:
        if chess.square_distance(square, king_square) <= 2:
            attackers = board.attackers(not color, square)
            danger += 0.05 * len(attackers)

    # 3. Penalize missing pawn shield (simple version)
    pawn_shield_files = [file - 1, file, file + 1]
    for f in pawn_shield_files:
        if 0 <= f <= 7:
            shield_square = chess.square(f, rank + (1 if color == chess.WHITE else -1))
            if not board.piece_at(shield_square):
                danger += 0.05

    # Clamp to [0, 1]
    return min(danger, 1.0)

def piece_activity(board: chess.Board, color: chess.Color) -> float:
    """
    Returns a value between 0.0 and 1.0 indicating how active the given side's pieces are.
    Higher = more active pieces.
    """

    activity = 0.0
    piece_count = 0

    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in board.pieces(piece_type, color):
            piece_count += 1

            # Mobility: how many squares this piece attacks
            attacks = board.attacks(square)
            activity += 0.02 * len(attacks)

            # Bonus for central influence
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            if 2 <= rank <= 5 and 2 <= file <= 5:
                activity += 0.05

    if piece_count == 0:
        return 0.0

    # Normalize and clamp
    activity = activity / piece_count
    return min(activity, 1.0)

def sacrifice_tolerance(board: chess.Board, color: chess.Color) -> float:
    """
    Returns a value between 0.0 and 1.0 indicating how acceptable
    material sacrifice is for the given side.
    """

    # How unsafe is the opponent king?
    opponent = not color
    danger = king_safety(board, opponent)

    # How active are our pieces?
    activity = piece_activity(board, color)

    # Core intuition:
    # Sacrifices make sense only when BOTH are present
    tolerance = 0.6 * danger + 0.4 * activity

    return min(max(tolerance, 0.0), 1.0)

def immediate_material_loss(board: chess.Board, move: chess.Move) -> int:
    """
    Estimates immediate material loss after making a move.
    Returns positive value if material is likely lost immediately.
    """

    temp_board = board.copy()
    temp_board.push(move)

    loss = 0

    # Check if moved piece is now capturable
    moved_piece = board.piece_at(move.from_square)
    if moved_piece:
        attackers = temp_board.attackers(not board.turn, move.to_square)
        defenders = temp_board.attackers(board.turn, move.to_square)

        if attackers and len(attackers) > len(defenders):
            # Assign simple material values
            piece_value = {
                chess.PAWN: 1,
                chess.KNIGHT: 3,
                chess.BISHOP: 3,
                chess.ROOK: 5,
                chess.QUEEN: 9,
            }.get(moved_piece.piece_type, 0)

            loss += piece_value

    return loss

