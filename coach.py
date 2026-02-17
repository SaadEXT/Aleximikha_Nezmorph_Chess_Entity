"""
=====================================================================
Aleximikha – Central Coaching Brain (Version 1.1 Stable Architecture)
---------------------------------------------------------------------

Purpose:
    Unified orchestration layer for post-game intelligence.

Responsibilities:
    • Run 3x3 decisive analysis via ThreeByThreeAnalyzer
    • Detect 1 brilliant move
    • Generate human explanations via LLM
    • Update player profile metrics
    • Recommend adaptive puzzles
    • Generate growth-oriented session summary

Design Philosophy:
    - No evaluation logic here
    - No tactical logic here
    - Pure orchestration layer
    - Explicit dependencies
    - Fully documented
=====================================================================
"""

import chess
import chess.pgn
import io
from typing import Dict, List

from engine.three_by_three_analyzer import ThreeByThreeAnalyzer
from engine.player_profile import PlayerProfile
from engine.profile_manager import load_profile, save_profile
from engine.puzzle_selector import PuzzleSelector
from engine.llm_backend import generate_llm_response


class Coach:
    """
    Central coordination system for Aleximikha’s training intelligence.

    This class does NOT perform evaluation or search.
    It delegates analysis to ThreeByThreeAnalyzer and
    converts results into a structured coaching report.
    """

    def __init__(self, player_id: str = "default_player"):
        """
        Initialize Coach system.

        Args:
            player_id (str): Unique identifier for player profile.
        """
        self.player_id = player_id
        self.profile: PlayerProfile = load_profile(player_id)
        self.analyzer = ThreeByThreeAnalyzer()
        self.puzzle_selector = PuzzleSelector()

    # =========================================================
    # PUBLIC ENTRY POINT
    # =========================================================

    def process_completed_game(self, pgn_string: str) -> Dict:
        """
        Full post-game coaching pipeline.

        Steps:
            1. Run 3x3 decisive analysis
            2. Generate LLM explanations
            3. Update player metrics
            4. Recommend puzzles
            5. Create session summary

        Returns:
            Dict: Structured coaching report.
        """

        # -----------------------------------------
        # 1. Run 3x3 Analyzer
        # -----------------------------------------
        analysis_report = self.analyzer.analyze_game(pgn_string)

        decisive_moments = analysis_report["critical_moments"]
        brilliant_move = analysis_report["brilliant_move"]

        # -----------------------------------------
        # 2. LLM Explanation Layer
        # -----------------------------------------
        explained_moments = [
            self._generate_explanation(moment)
            for moment in decisive_moments
        ]

        brilliant_explanation = None
        if brilliant_move:
            brilliant_explanation = self._generate_brilliant_explanation(
                brilliant_move
            )

        # -----------------------------------------
        # 3. Profile Update
        # -----------------------------------------
        weakest_area = self._update_profile(decisive_moments)

        # -----------------------------------------
        # 4. Puzzle Recommendation
        # -----------------------------------------
        recommended_puzzles = self.puzzle_selector.recommend(weakest_area)

        # -----------------------------------------
        # 5. Session Summary
        # -----------------------------------------
        summary = self._generate_session_summary(
            decisive_moments,
            brilliant_move,
            weakest_area
        )

        save_profile(self.profile)

        return {
            "critical_moments": explained_moments,
            "brilliant_move": brilliant_explanation,
            "weakest_area": weakest_area,
            "recommended_puzzles": recommended_puzzles,
            "summary": summary
        }

    # =========================================================
    # INTERNAL METHODS
    # =========================================================

    def _generate_explanation(self, moment: Dict) -> Dict:
        """
        Generate immersive LLM explanation for decisive mistake.
        """

        prompt = f"""
You are Aleximikha, an elite chess mentor.

Position FEN:
{moment["fen"]}

Player move:
{moment["move"]}

Evaluation swing:
{moment["swing"]}

Explain clearly:
1. Why the player likely played this move.
2. Why it was not ideal.
3. What stronger alternative existed and why.
Be instructive, immersive, and psychologically insightful.
"""

        response = generate_llm_response(prompt)

        return {
            "move_number": moment["move_number"],
            "fen": moment["fen"],
            "move": moment["move"],
            "swing": moment["swing"],
            "explanation": response
        }

    def _generate_brilliant_explanation(self, moment: Dict) -> Dict:
        """
        Generate explanation for the single brilliant move.
        """

        prompt = f"""
You are Aleximikha, an elite chess mentor.

Position FEN:
{moment["fen"]}

Brilliant move:
{moment["move"]}

Explain:
- Why this move is brilliant.
- What deep idea it contains.
- Why alternatives were inferior.
Make it inspiring yet technically grounded.
"""

        response = generate_llm_response(prompt)

        return {
            "move_number": moment["move_number"],
            "fen": moment["fen"],
            "move": moment["move"],
            "explanation": response
        }

    def _update_profile(self, decisive_moments: List[Dict]) -> str:
        """
        Update player metrics based on detected weaknesses.
        """

        weakness_counter = {}

        for moment in decisive_moments:
            area = moment.get("category", "general")
            weakness_counter[area] = weakness_counter.get(area, 0) + 1

        weakest_area = (
            max(weakness_counter, key=weakness_counter.get)
            if weakness_counter
            else "general"
        )

        self.profile.update_metric(weakest_area)

        return weakest_area
    
    # =========================================================
    # PUBLIC BACKWARD-COMPATIBILITY WRAPPER
    # =========================================================

    def full_game_review(self, pgn_string: str):
        """
        Backward-compatible public API expected by tests
        and legacy entry points.

        Internally delegates to process_completed_game().
        """

        return self.process_completed_game(pgn_string)

    def _generate_session_summary(
        self,
        decisive_moments: List[Dict],
        brilliant_move: Dict,
        weakest_area: str
    ) -> str:
        """
        Generate concise, growth-focused session summary.
        """

        return f"""


             
Session Complete.

Decisive Moments Reviewed: {len(decisive_moments)}
Brilliant Move Found: {"Yes" if brilliant_move else "No"}
Primary Growth Area: {weakest_area}

Your training model has been updated.
Consistency builds mastery.
"""
