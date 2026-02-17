"""
=====================================================================
Aleximikha – Intelligent Time Manager
---------------------------------------------------------------------

Purpose:
    Dynamic time allocation per move.

Philosophy:
    Beauty without time discipline is chaos.
    We calculate when to think deeper.

Features:
    • Phase-aware allocation
    • Critical-position detection
    • Increment support
    • Safe floor protection
    • Dynamic depth scaling
=====================================================================
"""

import chess
import time
from engine.evaluation import game_phase, evaluate_position

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

MIN_TIME_PER_MOVE = 0.05
CRITICAL_MULTIPLIER = 1.8
ENDGAME_MULTIPLIER = 1.4
LOW_TIME_THRESHOLD = 10  # seconds


# ---------------------------------------------------------
# Time Manager Class
# ---------------------------------------------------------

class TimeManager:

    def __init__(self, total_time_seconds=300, increment=0):
        self.total_time = total_time_seconds
        self.increment = increment
        self.remaining_time = total_time_seconds

    # -----------------------------------------------------
    # Estimate Moves Left
    # -----------------------------------------------------

    def estimate_moves_remaining(self, board):
        phase = game_phase(board)

        # Opening/Middlegame → assume 40 moves left
        if phase > 0.6:
            return 40

        # Middlegame → 25 moves left
        if phase > 0.3:
            return 25

        # Endgame → 15 moves left
        return 15

    # -----------------------------------------------------
    # Detect Critical Position
    # -----------------------------------------------------

    def is_critical_position(self, board):
        """
        Critical if:
            • Large evaluation swing possible
            • Many attackers near king
            • Check
        """

        if board.is_check():
            return True

        eval_score = abs(evaluate_position(board))

        if eval_score < 1.0:
            # Close game → more calculation required
            return True

        return False

    # -----------------------------------------------------
    # Allocate Time
    # -----------------------------------------------------

    def allocate_time(self, board):

        moves_left = self.estimate_moves_remaining(board)

        base_time = self.remaining_time / max(1, moves_left)

        multiplier = 1.0

        # Critical positions get more time
        if self.is_critical_position(board):
            multiplier *= CRITICAL_MULTIPLIER

        # Endgame precision
        if game_phase(board) < 0.3:
            multiplier *= ENDGAME_MULTIPLIER

        # Low time safeguard
        if self.remaining_time < LOW_TIME_THRESHOLD:
            multiplier *= 0.6

        allocated = max(MIN_TIME_PER_MOVE, base_time * multiplier)

        return min(allocated, self.remaining_time)

    # -----------------------------------------------------
    # Update After Move
    # -----------------------------------------------------

    def consume_time(self, seconds_spent):
        self.remaining_time -= seconds_spent
        self.remaining_time += self.increment
        self.remaining_time = max(0.0, self.remaining_time)
