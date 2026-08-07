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
            # protect against malformed JSON by checking if the loaded data is a list
            data = json.load(file)
            if isinstance(data, list):
                return data  # return the list of battle records
            return []  # if the data is not a list, return an empty list
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


def add_result(result, turns, hero_hp_left, hero_hp_max, enemy_name, path=None):
    """Add a battle result to the scores file, including date and relevant stats."""

    # get the path to the scores file, defaulting to SCORES_FILE if not provided
    path = path or SCORES_FILE

    # load existing records, append the new result, and save back to the file
    records = load_scores(path)
    records.append({
        "date": datetime.now().isoformat(timespec="seconds"),
        "result": result,
        "turns": turns,
        "hero_hp_left": hero_hp_left,
        "hero_hp_max": hero_hp_max,
        "enemy_name": enemy_name,
    })
    save_scores(records, path)


def summary(path=None):
    """Return a summary of battle results, including total battles, wins, losses, and most common enemy."""

    # get the path to the scores file, defaulting to SCORES_FILE if not provided
    path = path or SCORES_FILE

    # load existing records
    records = load_scores(path)

    # count the occurrences of each result type (victory, defeat, fled)
    counts = Counter(r["result"] for r in records)  # Counter will return 0 for missing keys, so we can safely access counts["victory"], etc.

    # calculate total battles, wins, and losses
    total_battles = len(records)
    victories = counts["victory"]
    defeats = counts["defeat"]
    flees = counts["fled"]

    # determine the most common enemy encountered
    enemy_counter = Counter(r["enemy_name"] for r in records)
    most_common_enemy = enemy_counter.most_common(1)[0][0] if enemy_counter else None

    return {
        "total_battles": total_battles,
        "victories": victories,
        "defeats": defeats,
        "flees": flees,
        "most_common_enemy": most_common_enemy,
    }
