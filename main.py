"""
=====================================================================
Aleximikha – Version 1 Entry Point
---------------------------------------------------------------------

Responsibilities:
    • Load pretrained neural model
    • Launch play session
    • Trigger 3x3 Tutor analysis
    • No training logic
    • Production-ready structure

=====================================================================
"""

import torch
import os

from engine.model import HumanMoveNet
from engine.play import PlaySession
from engine.coach import Coach  # 3x3 + Brilliant move system


MODEL_PATH = "aleximikha_style_v3.pt"


# =========================================================
# MODEL LOADER
# =========================================================

def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}\n"
            "Train the model first using train.train_model"
        )

    print("Loading neural model...")

    model = HumanMoveNet()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    print("Model loaded successfully.")
    return model


# =========================================================
# RUN GAME
# =========================================================

def run_game():

    model = load_model()

    session = PlaySession(model, tutor_enabled=False)
    pgn_string = session.play()

    # 3x3 + Brilliant Move Coach
    choice = input("\nRun Aleximikha 3x3 Deep Coach Review? (y/n): ").strip().lower()

    if choice == "y":

        coach = Coach(model=model)
        report = coach.full_game_review(pgn_string)

        print("\n========== 3x3 Critical Moments ==========\n")

        for moment in report["critical_moments"]:
            print(f"\nMove {moment['move_number']} – {moment['move']}")
            print("Evaluation Swing:", round(moment["swing"], 2))
            print("\nWhy you played it:")
            print(moment["why_played"])
            print("\nWhy it was not ideal:")
            print(moment["why_not_ideal"])
            print("\nWhat was better:")
            print(moment["better_move_explanation"])
            print("-" * 50)

        if report["brilliant_move"]:
            bm = report["brilliant_move"]
            print("\n========== Brilliant Move ==========\n")
            print(f"Move {bm['move_number']} – {bm['move']}")
            print(bm["explanation"])

        print("\n========== Growth Summary ==========\n")
        print(report["summary"])

    else:
        print("\nSession complete.")


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":
    run_game()


'''
_____________________________________________________________________________________________________________________

"📄 main.py

Purpose

This is the entry point, not the brain.

main.py answers:

“What happens when someone runs the engine?”

It orchestrates:

Data loading
Training
Testing
(Later) play mode, analysis mode

What main.py is allowed to do

✅ Call functions from other modules
✅ Decide when something happens
✅ Glue components together

What main.py must NEVER do

❌ Implement chess logic
❌ Implement neural logic
❌ Contain complex algorithms

If logic grows here → architecture is rotting."

main.py
 ├── data/        (reads data)
 ├── train/       (triggers training)
 └── engine/      (uses the brain)

 ______________________________________________________________________________________________________________________

 📄 main.py — THE ORCHESTRATION LAYER
Purpose (in one sentence)

main.py is the conductor of the system: it decides what happens, in what order,
and in which mode — without doing any real work itself.

If the project were an orchestra:

engine/ = musicians
train/ = music school
data/ = sheet music
main.py = the conductor

Why main.py exists

Every non-trivial system needs a single, obvious entry point.

main.py answers:

“What does this program actually do when I run it?”

Without this file:

Logic becomes scattered
Execution paths become unclear
UI / CLI / API flows become tangled
So we centralize flow, not logic.

What main.py is ALLOWED to do

✅ Import from engine/
✅ Import from train/
✅ Import from data/ (indirectly via loaders)
✅ Decide when training happens
✅ Decide when inference happens
✅ Choose modes (train / play / analyze)

Think of it as policy, not mechanics.

What main.py must NEVER do

❌ Implement chess rules
❌ Implement neural networks
❌ Encode boards
❌ Select moves
❌ Define learning algorithms

If you ever see:

loops doing learning math
chess logic
tensor manipulation
inside main.py → architecture violation 🚨

Current Responsibility (Phase 1–2)

Right now, main.py performs three high-level tasks:

Load human games
Build a learning dataset
Trigger training

That’s it.

Current Execution Flow (Phase 2)

Conceptually, main.py does this:

START PROGRAM
   ↓
Load PGN games
   ↓
Extract (position → move) samples
   ↓
Train neural model
   ↓
Exit


This is offline learning mode, not gameplay.

Annotated Example (Conceptual, not code rewrite)

Here’s how we think about the current main.py:

# 1. Acquire raw human knowledge
games = load_games(...)

# 2. Convert human games into learning material
dataset = extract_positions(games)

# 3. Teach the engine its preferences
model = train_model(dataset)

# 4. Confirm learning is complete
print("Neural soul injected.")


Notice:

No chess logic
No neural math
No decision-making

Only coordination.

Interaction Map (VERY IMPORTANT)
main.py
 ├── engine/game_loader.py   → loads PGNs
 ├── train/dataset.py        → builds samples
 ├── train/train.py          → trains model
 └── engine/model.py         → receives learned weights


All arrows point away from main.py.

Nothing points into it.
That’s correct.

Why main.py is the safest place to grow features

Future additions that belong here:

Mode selection:

train
play vs engine
analysis
CLI flags
UI hooks
API endpoints
Session management

Why?
Because these are workflow concerns, not intelligence.

What main.py will become later (important foresight)

Eventually, this file will evolve into something like:

if mode == TRAIN:
    train_engine()

elif mode == PLAY:
    run_game_loop()

elif mode == ANALYZE:
    analyze_position()


But:

The logic inside those functions still lives elsewher
main.py just chooses which story to tell

Architectural Rule (LOCK THIS)

If you don’t know where new code belongs, it does NOT belong in main.py.

You decide the home first.
Then you write code.

This rule alone prevents 80% of architecture decay.

'''