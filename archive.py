"""
=====================================================================
Aleximikha – Games Archive System
---------------------------------------------------------------------

Stores completed games locally in JSON format.

Each game entry contains:
    • PGN
    • Result
    • Mode (Play / Analysis / Tutor)
    • Move count
    • Timestamp
=====================================================================
"""

import os
import json
from datetime import datetime
from typing import List, Dict


ARCHIVE_FILE = "aleximikha_games_archive.json"


# ------------------------------------------------------------
# Internal Helpers
# ------------------------------------------------------------

def _load_raw() -> List[Dict]:
    if not os.path.exists(ARCHIVE_FILE):
        return []

    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(data: List[Dict]):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def save_game(pgn: str, result: str, mode: str, move_count: int):
    """
    Save completed game to archive.
    """

    data = _load_raw()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "result": result,
        "move_count": move_count,
        "pgn": pgn
    }

    data.append(entry)
    _save_raw(data)


def load_games() -> List[Dict]:
    """
    Return list of saved games.
    """
    return _load_raw()


def clear_archive():
    """
    Clear all stored games.
    """
    _save_raw([])
