# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Persistent battle records stored as a local JSON file.

Holds: load/save helpers for the scores file, add_result to record each
battle outcome, and summary statistics. The module works with plain values,
so it knows nothing about the Battle or Character classes.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

SCORES_FILE = Path(__file__).resolve().parent / "scores.json"

def load_scores(path=None):
    """Load scores from the JSON file, returning a list of battle records or an empty list."""

    # get the path to the scores file, defaulting to SCORES_FILE if not provided
    path = path or SCORES_FILE

    # if the file does not exist, return an empty list to indicate no scores are available
    if not path.exists():
        return []

    # open the file and load the JSON data, handling any potential errors gracefully
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_scores(records, path=None):
    """Save the list of battle records to the JSON file."""

    # get the path to the scores file, defaulting to SCORES_FILE if not provided
    path = path or SCORES_FILE

    # open the file and write the JSON data, handling any potential errors gracefully
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=2)
    except OSError:
        pass  # ignore errors for now; could log or raise an exception in a real application
