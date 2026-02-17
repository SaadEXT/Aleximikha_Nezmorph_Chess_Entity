"""
=====================================================================
Aleximikha – Interactive Tutor Mode v2
---------------------------------------------------------------------

Romantic Grandmaster Coaching System

Purpose:
    Live coaching during play with phase awareness,
    attack-pressure sensitivity, and evolving player profiling.

Philosophy:
    Not interruption.
    Not sterile evaluation spam.
    But intelligent, adaptive mentorship.

New Features (v2):
    • Phase detection (Opening / Middlegame / Endgame)
    • Attack-pressure commentary integration
    • Player error tracking
    • Structured performance metrics
    • Improved documentation
    • Preserves all previous functionality

=====================================================================
"""

import chess
import math

from engine.evaluation import (
    evaluate_position,
    evaluate_attack_pressure,
    game_phase,
    search,
)


# =========================================================
# CONFIGURATION
# =========================================================

TUTOR_DEPTH = 4

BLUNDER_THRESHOLD = 2.5
MISTAKE_THRESHOLD = 1.2
INACCURACY_THRESHOLD = 0.6


# =========================================================
# INTERACTIVE TUTOR CLASS
# =========================================================

class InteractiveTutor:
    """
    Romantic Grandmaster Mentor.

    Tracks:
        - Evaluation swings
        - Missed best move value
        - Phase-specific weaknesses
        - Tactical vs positional errors
        - Attack neglect patterns

    Designed for progressive refinement.
    """

    def __init__(self):

        # Memory metrics
        self.total_moves = 0
        self.blunders = 0
        self.mistakes = 0
        self.inaccuracies = 0

        self.attack_neglect_count = 0
        self.endgame_precision_issues = 0

        self.phase_error_map = {
            "opening": 0,
            "middlegame": 0,
            "endgame": 0,
        }

    # =====================================================
    # PHASE DETECTION
    # =====================================================

    def detect_phase(self, board):
        """
        Determines game phase using material phase scaling.
        """
        phase = game_phase(board)

        if phase > 0.75:
            return "opening"
        elif phase > 0.35:
            return "middlegame"
        else:
            return "endgame"

    # =====================================================
    # MAIN EVALUATION ENTRY
    # =====================================================

    def evaluate_player_move(self, board_before, move_played):
        """
        Evaluates player's move live.

        Returns:
            Romantic coaching feedback string.
        """

        self.total_moves += 1

        board = board_before.copy()

        eval_before = evaluate_position(board)
        attack_before = evaluate_attack_pressure(board)

        # Engine best move
        best_move, best_score = self.find_best_move(board)

        # Play player's move
        board.push(move_played)

        eval_after = evaluate_position(board)
        attack_after = evaluate_attack_pressure(board)

        swing = eval_after - eval_before
        missed_value = best_score - eval_after
        attack_drop = attack_before - attack_after

        phase = self.detect_phase(board_before)

        return self.generate_feedback(
            board_before,
            move_played,
            swing,
            missed_value,
            best_move,
            attack_drop,
            phase
        )

    # =====================================================
    # ENGINE BEST MOVE SEARCH
    # =====================================================

    def find_best_move(self, board):
        """
        Finds best move using depth-limited negamax search.
        """

        best_value = -math.inf
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            value = -search(board, TUTOR_DEPTH - 1, -math.inf, math.inf)
            board.pop()

            if value > best_value:
                best_value = value
                best_move = move

        return best_move, best_value

    # =====================================================
    # FEEDBACK GENERATOR
    # =====================================================

    def generate_feedback(
        self,
        board_before,
        move,
        swing,
        missed_value,
        best_move,
        attack_drop,
        phase
    ):
        """
        Core commentary logic with phase + attack awareness.
        """

        abs_swing = abs(swing)

        # Track error severity
        if abs_swing >= BLUNDER_THRESHOLD:
            self.blunders += 1
            self.phase_error_map[phase] += 1

        elif abs_swing >= MISTAKE_THRESHOLD:
            self.mistakes += 1
            self.phase_error_map[phase] += 1

        elif abs_swing >= INACCURACY_THRESHOLD:
            self.inaccuracies += 1

        # Attack neglect detection
        if attack_drop > 0.5:
            self.attack_neglect_count += 1

        if phase == "endgame" and abs_swing >= MISTAKE_THRESHOLD:
            self.endgame_precision_issues += 1

        # =================================================
        # Romantic Feedback Construction
        # =================================================

        # Severe missed winning move
        if missed_value >= BLUNDER_THRESHOLD:
            return (
                f"{move.uci()}… bold, but destiny was closer.\n"
                f"The move {best_move.uci()} carried far greater force.\n"
                f"In the {phase}, precision is power."
            )

        # Attack neglect
        if attack_drop > 0.5:
            return (
                f"{move.uci()} softens your attacking momentum.\n"
                "When the enemy king trembles, hesitation is costly.\n"
                "Press when the position burns."
            )

        # Blunder
        if abs_swing >= BLUNDER_THRESHOLD:
            return (
                f"{move.uci()}… a leap into fog.\n"
                "Calculate deeper before committing.\n"
                f"In the {phase}, such slips reshape the battle."
            )

        # Mistake
        if abs_swing >= MISTAKE_THRESHOLD:
            return (
                f"{move.uci()} shows ambition — "
                "yet the position demanded sharper precision."
            )

        # Inaccuracy
        if abs_swing >= INACCURACY_THRESHOLD:
            return (
                f"{move.uci()} is playable. "
                "But harmony was within reach."
            )

        # Praise
        return (
            f"{move.uci()} — strong. Purposeful.\n"
            "You are beginning to command the position."
        )

    # =====================================================
    # HINT SYSTEM
    # =====================================================

    def give_hint(self, board):
        """
        Provides strategic hint without revealing move.
        """

        best_move, _ = self.find_best_move(board)
        piece = board.piece_at(best_move.from_square)

        if piece:
            return (
                f"Reconsider your {piece.symbol().upper()} — "
                "it carries untapped energy."
            )

        return "There exists a sharper continuation here."

    # =====================================================
    # PERFORMANCE SUMMARY
    # =====================================================

    def performance_summary(self):
        """
        Returns structured coaching diagnostics.
        """

        return {
            "total_moves": self.total_moves,
            "blunders": self.blunders,
            "mistakes": self.mistakes,
            "inaccuracies": self.inaccuracies,
            "attack_neglect": self.attack_neglect_count,
            "endgame_precision_issues": self.endgame_precision_issues,
            "phase_errors": self.phase_error_map
        }
