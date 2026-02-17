"""
=====================================================================
Aleximikha – Tensor → Board Decoder
---------------------------------------------------------------------

Purpose:
    Reconstruct chess.Board from encoded tensor.

Assumes:
    12 x 8 x 8 tensor
    Planes:
        0-5   White P N B R Q K
        6-11  Black P N B R Q K

Used by:
    Puzzle mining
    Dataset validation
    Self-evolution modules
=====================================================================
"""

import chess
import torch


PIECE_MAP = {
    0: (chess.PAWN, chess.WHITE),
    1: (chess.KNIGHT, chess.WHITE),
    2: (chess.BISHOP, chess.WHITE),
    3: (chess.ROOK, chess.WHITE),
    4: (chess.QUEEN, chess.WHITE),
    5: (chess.KING, chess.WHITE),
    6: (chess.PAWN, chess.BLACK),
    7: (chess.KNIGHT, chess.BLACK),
    8: (chess.BISHOP, chess.BLACK),
    9: (chess.ROOK, chess.BLACK),
    10: (chess.QUEEN, chess.BLACK),
    11: (chess.KING, chess.BLACK),
}


def reconstruct_board_from_tensor(board_tensor):
    """
    Reconstructs a chess.Board object from encoded tensor.

    Args:
        board_tensor: Tensor or numpy array (12, 8, 8)

    Returns:
        chess.Board object
    """

    if isinstance(board_tensor, torch.Tensor):
        board_tensor = board_tensor.cpu().numpy()

    board = chess.Board(None)  # start with empty board

    for plane_idx in range(12):

        piece_type, color = PIECE_MAP[plane_idx]

        for rank in range(8):
            for file in range(8):

                if board_tensor[plane_idx][rank][file] == 1:

                    square = chess.square(file, 7 - rank)
                    piece = chess.Piece(piece_type, color)
                    board.set_piece_at(square, piece)

    # Default assumptions
    board.turn = chess.WHITE
    board.castling_rights = chess.BB_EMPTY
    board.ep_square = None

    return board

