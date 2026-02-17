"""
=====================================================================
Aleximikha – Player Profiling Engine v1
---------------------------------------------------------------------

Purpose:
    Persistent longitudinal intelligence about a human player.

Philosophy:
    Not punishment.
    Not harsh rating drops.
    But gradual refinement through patterns.

Tracks:
    • Tactical awareness
    • Endgame technique
    • King safety discipline
    • Positional understanding
    • Calculation accuracy
    • Aggression balance

Persistence:
    Automatically loads/saves to:
        data/player_profile.json

Design:
    • Smooth metric updates
    • Long-term averaging
    • Fully extensible architecture
=====================================================================
"""

import os
import json
from typing import Dict


# =========================================================
# CONFIGURATION
# =========================================================

PROFILE_PATH = os.path.join("data", "player_profile.json")

DEFAULT_PROFILE = {
    "games_played": 0,
    "tactical_awareness": 50.0,
    "endgame_technique": 50.0,
    "king_safety": 50.0,
    "positional_understanding": 50.0,
    "calculation_accuracy": 50.0,
    "aggression_balance": 50.0
}

MIN_SCORE = 0.0
MAX_SCORE = 100.0
SMOOTHING_FACTOR = 0.08  # Controls gradual change


# =========================================================
# Utility
# =========================================================

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


# =========================================================
# Player Profile Class
# =========================================================

class PlayerProfile:
    """
    Persistent player intelligence model.

    Usage:
        profile = PlayerProfile()
        profile.update_from_game(game_report)
        profile.save()
    """

    def __init__(self):
        self.profile: Dict[str, float] = self._load_profile()

    # -----------------------------------------------------
    # Load / Save
    # -----------------------------------------------------

    def _load_profile(self) -> Dict[str, float]:

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(PROFILE_PATH):
            self._save_profile(DEFAULT_PROFILE)
            return DEFAULT_PROFILE.copy()

        try:
            with open(PROFILE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            # Fallback to default if corrupted
            self._save_profile(DEFAULT_PROFILE)
            return DEFAULT_PROFILE.copy()

    def _save_profile(self, data: Dict[str, float]):

        with open(PROFILE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def save(self):
        self._save_profile(self.profile)

    # -----------------------------------------------------
    # Metric Update Logic
    # -----------------------------------------------------

    def _adjust_metric(self, key: str, delta: float):
        """
        Smooth metric update.
        Uses exponential smoothing rather than harsh shifts.
        """

        current = self.profile.get(key, 50.0)
        new_value = current + (delta * SMOOTHING_FACTOR)

        self.profile[key] = clamp(new_value, MIN_SCORE, MAX_SCORE)

    # -----------------------------------------------------
    # Public Game Update Entry Point
    # -----------------------------------------------------

    def update_from_game(self, game_report: Dict):
        """
        Updates profile based on tutor game report.

        Expects:
            game_report = {
                "blunders": int,
                "mistakes": int,
                "inaccuracies": int,
                "endgame_errors": int,
                "king_exposure_events": int,
                "aggressive_overpushes": int,
                "accurate_sequences": int
            }
        """

        self.profile["games_played"] += 1

        blunders = game_report.get("blunders", 0)
        mistakes = game_report.get("mistakes", 0)
        inaccuracies = game_report.get("inaccuracies", 0)
        endgame_errors = game_report.get("endgame_errors", 0)
        king_issues = game_report.get("king_exposure_events", 0)
        overpush = game_report.get("aggressive_overpushes", 0)
        accurate = game_report.get("accurate_sequences", 0)

        # Tactical awareness
        tactical_delta = accurate - (blunders * 2 + mistakes)
        self._adjust_metric("tactical_awareness", tactical_delta)

        # Endgame technique
        self._adjust_metric("endgame_technique", -endgame_errors)

        # King safety
        self._adjust_metric("king_safety", -king_issues)

        # Positional understanding
        positional_delta = accurate - inaccuracies
        self._adjust_metric("positional_understanding", positional_delta)

        # Calculation accuracy
        calc_delta = accurate - blunders
        self._adjust_metric("calculation_accuracy", calc_delta)

        # Aggression balance
        aggression_delta = -overpush
        self._adjust_metric("aggression_balance", aggression_delta)

        self.save()

    # -----------------------------------------------------
    # Insight Generation
    # -----------------------------------------------------

    def weakest_area(self) -> str:
        """
        Returns the weakest metric for adaptive training.
        """

        metrics = {
            k: v for k, v in self.profile.items()
            if k != "games_played"
        }

        return min(metrics, key=metrics.get)

    def strongest_area(self) -> str:
        """
        Returns strongest trait.
        """

        metrics = {
            k: v for k, v in self.profile.items()
            if k != "games_played"
        }

        return max(metrics, key=metrics.get)

    # -----------------------------------------------------
    # Read-only Access
    # -----------------------------------------------------

    def get_profile(self) -> Dict[str, float]:
        return self.profile.copy()
