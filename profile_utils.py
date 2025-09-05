from __future__ import annotations

"""Helpers for saving and loading simple player profiles.

The original project stored a JSON file next to the game.  In this refactored
version the behaviour is kept the same, but the functions live in their own
module so that new programmers can clearly see what code is responsible for
persistence.
"""

import json
import os

# Default file name used by :func:`load_profile` and :func:`save_profile`.
PROFILE_FILE = "user_profile.json"


def load_profile(path: str = PROFILE_FILE) -> dict:
    """Return the profile stored in *path*.

    The function is intentionally defensive: if the file does not exist or
    contains invalid JSON we return a fresh profile with only the first level
    unlocked.  Each profile dictionary contains at least the key
    ``"highest_level"``.
    """

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            # Treat any read/parse error as if the file did not exist.
            data = {"highest_level": 1}
    else:
        data = {"highest_level": 1}

    # Older files might miss the ``highest_level`` key – guarantee its
    # presence for callers.
    if "highest_level" not in data:
        data["highest_level"] = 1
    return data


def save_profile(data: dict, path: str = PROFILE_FILE) -> None:
    """Persist *data* as JSON at *path*.

    The profile is very small so we simply dump it in one go.  Errors bubble
    up to the caller which keeps this helper nice and short for beginners to
    read.
    """

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def unlock_next_level(profile: dict, current_level: int) -> None:
    """Unlock the level following ``current_level`` in ``profile``.

    ``profile`` is modified in place.  The highest unlocked level only
    increases when the current level is at least as high as the previously
    unlocked one.  Levels above 20 are ignored because the game only contains
    twenty in total.
    """

    highest = profile.get("highest_level", 1)
    if current_level >= highest and current_level < 20:
        profile["highest_level"] = current_level + 1
