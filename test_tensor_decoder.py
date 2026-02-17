import chess
from engine.encoder import encode_board
from train.tensor_decoder import reconstruct_board_from_tensor

# Create initial board
board = chess.Board()

# Encode it
tensor = encode_board(board)

# Decode it
new_board = reconstruct_board_from_tensor(tensor)

print("Original Board:")
print(board)
print("\nReconstructed Board:")
print(new_board)

print("\nBoards equal?")
print(board.board_fen() == new_board.board_fen())
