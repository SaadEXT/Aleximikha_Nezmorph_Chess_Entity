import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import chess

from engine.analysis import analyze_position
from engine.game_loader import load_games
from train.dataset import extract_positions
from train.train import train_model


games = load_games("data/pgn/tal.pgn", max_games=1)
dataset = []

for game in games:
    dataset.extend(extract_positions(game))

model = train_model(dataset, epochs=1)

board = chess.Board()
move, explanation = analyze_position(board, model)

print("Suggested move:", move)
print("Explanation:")
for line in explanation:
    print("-", line)
