# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Central logging setup for diagnostics."""

import logging
from paths import game_dir


def setup_logging() -> None:
    """Write a diagnostic log next to the news cache in the user data dir."""
    logging.basicConfig(
        filename=game_dir().parent / "launcher.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,  # re-configure if someone called basicConfig before
    )
