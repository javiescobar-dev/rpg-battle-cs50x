# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Persist user settings for the launcher (currently the theme)."""

import json
from pathlib import Path
from paths import game_dir


def settings_path() -> Path:
    """Return the path to the launcher settings file."""
    return game_dir().parent / "settings.json"


def load_theme() -> str:
    """Return the saved theme ('Light' or 'Dark'), defaulting to 'Light'."""
    try:
        # load theme from settings.json
        if settings_path().exists():
            # read and parse settings.json
            data = json.loads(settings_path().read_text())
            # if theme exists and is valid, return it (prevents errors if settings.json is corrupted)
            if data.get("theme") in ("Light", "Dark"):
                return data["theme"]
    except Exception:
        # pass if any exception occurs
        pass
    # return default theme in case of error or if settings.json does not exist
    return "Light"


def save_theme(theme: str) -> None:
    """Persist the given theme ('Light' or 'Dark') to disk."""
    # save theme to settings.json
    settings_path().write_text(json.dumps({"theme": theme}))
