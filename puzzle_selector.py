"""
=====================================================================
Aleximikha – Unified Puzzle Selector (Version 1 Final)
---------------------------------------------------------------------

Purpose:
    Adaptive disk-based puzzle recommendation engine.

Features:
    • Reads from puzzles/ directory
    • Category-based selection
    • Weakness-driven filtering
    • Clean Coach integration
    • Scalable to 100k+ puzzles

Design:
    Class-based.
    No hardcoded puzzle lists.
=====================================================================
"""

import os
import random
from typing import List


PUZZLE_ROOT = "puzzles"


class PuzzleSelector:
    """
    Disk-based puzzle recommendation system.
    """

    def __init__(self, root_path: str = PUZZLE_ROOT):
        self.root_path = root_path

    # =========================================================
    # Public API
    # =========================================================

    def recommend(self, weakness: str, limit: int = 5) -> List[str]:
        """
        Recommend puzzles based on detected weakness.

        Args:
            weakness (str): Category name (e.g., tactical, endgame)
            limit (int): Number of puzzles to return

        Returns:
            List[str]: List of FEN strings
        """

        category_path = os.path.join(self.root_path, weakness)

        # Fallback if folder missing
        if not os.path.exists(category_path):
            category_path = os.path.join(self.root_path, "tactical")

        if not os.path.exists(category_path):
            return []

        fen_files = [
            os.path.join(category_path, f)
            for f in os.listdir(category_path)
            if f.endswith(".fen")
        ]

        if not fen_files:
            return []

        selected = random.sample(
            fen_files,
            min(limit, len(fen_files))
        )

        puzzles = []

        for file_path in selected:
            with open(file_path, "r") as f:
                puzzles.append(f.read().strip())

        return puzzles
