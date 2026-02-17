import chess

from engine.analysis import analyze_position
from engine.analysis_voice import narrate_analysis
from train.train import train_model
from train.dataset import extract_positions
from engine.game_loader import load_games


print("\n--- Analysis Voice Test ---")

# Load 1 game for fast model
games = load_games("data/pgn/tal.pgn", max_games=1)

dataset = []
for g in games:
    dataset.extend(extract_positions(g))

model = train_model(dataset, epochs=1)

board = chess.Board()

move, explanation = analyze_position(board, model)

spoken = narrate_analysis(move, explanation)

print("Move:", move.uci())
print("\nAleximikha says:")
print(spoken)
