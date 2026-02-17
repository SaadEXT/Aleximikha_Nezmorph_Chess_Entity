import chess.pgn

def load_games(pgn_path, max_games=100):
    games = []
    with open(pgn_path, encoding="utf-8") as pgn:
        while len(games) < max_games:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            games.append(game)
    return games


"""
_____________________________________________________________________________________________________________________

📄 engine/game_loader.py

Purpose

Responsible for reading chess games from PGN files.

It answers:

“How do we turn human games into engine-usable objects?”

Why this file exists separately

PGN parsing is:

Messy

Error-prone

External-data-facing

So we isolate it to:

Contain chaos

Handle malformed data gracefully

Prevent corruption spreading inward

What this file does

✅ Opens PGN files
✅ Iterates through games
✅ Returns clean chess.pgn.Game objects

What it does NOT do

❌ Encode boards
❌ Train models
❌ Select moves
❌ Apply style

It only loads, nothing else.

Interaction map
data/pgn/*.pgn
      ↓
engine/game_loader.py
      ↓
train/dataset.py


This file is a gateway, not a processor."""