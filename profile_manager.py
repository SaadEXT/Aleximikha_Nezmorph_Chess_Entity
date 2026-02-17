"""
=====================================================================
Aleximikha – Profile Persistence Manager
---------------------------------------------------------------------

Purpose:
    Save and load Tutor intelligence profiles.
    Maintain long-term learning memory.
=====================================================================
"""

import json
import os

PROFILE_DIR = "profiles"


def ensure_profile_dir():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)


def save_profile(username, tutor_profile):
    ensure_profile_dir()

    path = os.path.join(PROFILE_DIR, f"{username}.json")

    with open(path, "w") as f:
        json.dump(dict(tutor_profile.stats), f, indent=4)


def load_profile(username, tutor_profile=None):

    ensure_profile_dir()

    path = os.path.join(PROFILE_DIR, f"{username}.json")

    if not os.path.exists(path):
        return

    with open(path, "r") as f:
        data = json.load(f)

    for key, value in data.items():
        tutor_profile.stats[key] = value
