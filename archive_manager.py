"""
=====================================================================
Aleximikha – Game Archive Manager
---------------------------------------------------------------------

Purpose:
    Handle saving, listing, loading and replaying PGN games.

Features:
    • Auto-save completed games
    • Timestamped filenames
    • Safe directory creation
    • PGN loading
    • Replay support

Version 1 – Stable
=====================================================================
"""

import os
import datetime
import chess.pgn
import io
from typing import List


ARCHIVE_DIR = "archive"


class ArchiveManager:
    """
    Handles persistent game storage.
    """

    def __init__(self, directory: str = ARCHIVE_DIR):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    # =========================================================

    def save_game(self, pgn_string: str) -> str:
        """
        Save PGN string to disk with timestamp filename.
        Returns file path.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.pgn"
        filepath = os.path.join(self.directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(pgn_string)

        return filepath

    # =========================================================

    def list_games(self) -> List[str]:
        """
        Returns sorted list of archive filenames.
        """
        files = [
            f for f in os.listdir(self.directory)
            if f.endswith(".pgn")
        ]

        files.sort(reverse=True)
        return files

    # =========================================================

    def load_game(self, filename: str) -> str:
        """
        Load PGN content from file.
        """
        filepath = os.path.join(self.directory, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    # =========================================================

    def parse_game(self, pgn_string: str):
        """
        Convert PGN string to chess.pgn.Game object.
        """
        return chess.pgn.read_game(io.StringIO(pgn_string))
