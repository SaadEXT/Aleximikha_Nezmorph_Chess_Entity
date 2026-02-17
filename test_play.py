"""
test_play.py

Simple terminal play test.
"""

from train.train import train_model
from train.dataset import extract_positions
from engine.game_loader import load_games
from engine.play import PlaySession

# Train minimal model for testing
games = load_games("data/pgn/tal.pgn", max_games=1)
dataset = []
for g in games:
    dataset.extend(extract_positions(g))

model = train_model(dataset, epochs=1)

session = PlaySession(model)
pgn = session.play()

print("\nFinal PGN:\n")
print(pgn)

