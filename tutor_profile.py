"""
=====================================================================
Aleximikha – Tutor Intelligence Profiling System
---------------------------------------------------------------------

Purpose:
    Track player weaknesses across games.
    Recommend targeted training themes.

Features:
    • Phase-based weakness tracking
    • Tactical motif classification
    • Positional mistake tracking
    • Training recommendations
=====================================================================
"""

import chess
from collections import defaultdict

from engine.endgame import detect_endgame_phase


class TutorProfile:

    def __init__(self):
        self.stats = defaultdict(int)
        self.total_moves_analyzed = 0

    # =====================================================
    # Update Profile After Move
    # =====================================================

    def record_mistake(self, board_before, board_after, swing):

        phase = detect_endgame_phase(board_before)

        if abs(swing) < 0.5:
            return

        self.total_moves_analyzed += 1

        # Phase tracking
        self.stats[f"{phase}_errors"] += 1

        # Tactical classification
        if self.hanging_piece(board_after):
            self.stats["hanging_piece"] += 1

        if self.back_rank_weakness(board_after):
            self.stats["back_rank"] += 1

        if phase == "endgame":
            self.stats["endgame_technique"] += 1

    # =====================================================
    # Tactical Heuristics
    # =====================================================

    def hanging_piece(self, board):
        """
        Detect if a piece is attacked more times than defended.
        """
        for square, piece in board.piece_map().items():
            attackers = len(board.attackers(not piece.color, square))
            defenders = len(board.attackers(piece.color, square))

            if attackers > defenders and piece.piece_type != chess.KING:
                return True
        return False

    def back_rank_weakness(self, board):
        """
        Detect simple back rank vulnerability.
        """
        for color in [chess.WHITE, chess.BLACK]:
            king_sq = board.king(color)
            if king_sq is None:
                continue

            rank = chess.square_rank(king_sq)
            if (color == chess.WHITE and rank == 0) or \
               (color == chess.BLACK and rank == 7):

                if not any(
                    board.piece_at(sq) and
                    board.piece_at(sq).piece_type == chess.PAWN and
                    board.piece_at(sq).color == color
                    for sq in chess.SQUARES
                ):
                    return True
        return False

    # =====================================================
    # Weakness Report
    # =====================================================

    def generate_report(self):

        if self.total_moves_analyzed == 0:
            return "Insufficient data for profile analysis."

        weaknesses = sorted(
            self.stats.items(),
            key=lambda x: x[1],
            reverse=True
        )

        report = ["\n=== Tutor Profile Analysis ==="]

        for key, value in weaknesses[:5]:
            report.append(f"{key}: {value} occurrences")

        report.append("\nRecommended Training Focus:")
        report.extend(self.recommend_training())

        return "\n".join(report)

    # =====================================================
    # Training Recommendation Engine
    # =====================================================

    def recommend_training(self):

        recommendations = []

        if self.stats["opening_errors"] > 2:
            recommendations.append("• Opening development puzzles")

        if self.stats["middlegame_errors"] > 2:
            recommendations.append("• Tactical calculation puzzles")

        if self.stats["endgame_errors"] > 2:
            recommendations.append("• Rook and pawn endgames")

        if self.stats["hanging_piece"] > 2:
            recommendations.append("• Hanging piece awareness drills")

        if self.stats["back_rank"] > 1:
            recommendations.append("• Back rank defense training")

        if not recommendations:
            recommendations.append("• Balanced mixed training set")

        return recommendations
