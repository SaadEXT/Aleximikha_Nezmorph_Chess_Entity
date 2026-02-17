"""
=====================================================================
Aleximikha – Training Mode
---------------------------------------------------------------------

Purpose:
    Structured tactical and positional training.

Features:
    • Persistent player profile
    • Adaptive puzzle selection
    • Theme-based recommendations
    • Real-time validation
    • Difficulty scaling
    • Profile auto-save

No engine features removed.
This is an extension layer.
=====================================================================
"""

import chess
import random

from engine.tutor_profile import TutorProfile
from engine.profile_manager import save_profile, load_profile
from engine.puzzle_selector import select_puzzles


# =========================================================
# TRAINING SESSION
# =========================================================

class TrainingSession:

    def __init__(self, username="player"):

        self.username = username
        self.profile = TutorProfile()

        # Load persistent stats if available
        load_profile(username, self.profile)

        print("\n🎯 Training Mode Activated")
        print(f"Welcome back, {username}.")
        print("Let us refine your weaknesses.\n")

    # -----------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------

    def start(self):

        puzzles = select_puzzles(self.profile)

        if not puzzles:
            print("No puzzles available.")
            return

        for idx, puzzle in enumerate(puzzles, 1):

            print(f"\nPuzzle {idx}/{len(puzzles)}")
            print(f"Theme: {puzzle['theme']}")
            print(f"Difficulty: {puzzle['difficulty']}")

            board = chess.Board(puzzle["fen"])
            print(board)

            solved = self.solve_puzzle(board, puzzle)

            if solved:
                print("✔ Correct. Strong calculation.")
            else:
                print("✘ Incorrect.")
                print("Solution was:", puzzle["solution"])

        # Save profile after session
        save_profile(self.username, self.profile)

        print("\n📊 Session Complete.")
        self.print_profile_summary()

    # -----------------------------------------------------
    # SOLVER
    # -----------------------------------------------------

    def solve_puzzle(self, board, puzzle):

        attempts = 0
        max_attempts = 2

        while attempts < max_attempts:

            move_input = input("\nYour move (UCI): ").strip()

            try:
                move = chess.Move.from_uci(move_input)

                if move not in board.legal_moves:
                    print("Illegal move.")
                    continue

                if move.uci() == puzzle["solution"]:
                    self.profile.record_error("none")
                    return True

                else:
                    attempts += 1
                    print("Not quite. Try again.")

            except ValueError:
                print("Invalid format.")

        # Record weakness
        self.profile.record_error(puzzle["theme"])
        return False

    # -----------------------------------------------------
    # PROFILE SUMMARY
    # -----------------------------------------------------

    def print_profile_summary(self):

        if not self.profile.stats:
            print("No weaknesses recorded yet.")
            return

        print("\n📈 Weakness Tracking:")

        for theme, count in sorted(
            self.profile.stats.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {theme}: {count}")
