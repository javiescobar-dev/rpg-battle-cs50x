# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Turn-based battle engine. Pure logic with no rendering.

Will hold: the Battle class that resolves player and enemy turns, the damage
formulas, skill casting, potions, defending and fleeing, and the end
conditions (victory / defeat / fled).
"""

import random
from game.config import (
    SKILLS, DAMAGE_BASE, DAMAGE_RANDOM, CRIT_CHANCE, CRIT_MULTIPLIER,
    FLEE_BASE, FLEE_SPEED_WEIGHT, FLEE_MIN, FLEE_MAX,
    RESULT_VICTORY, RESULT_DEFEAT, RESULT_FLED,
)

class Battle:
    """Turn-based battle engine: resolves player and enemy turns and damage."""

    def __init__(self, hero, enemy):
        self.hero = hero
        self.enemy = enemy
        self.result = None  # Will hold the result of the battle (victory, defeat, fled)
        self.log = []       # Log of actions taken during the battle
        self.turns = 0      # Count of turns taken in the battle


    def is_finished(self):
        """Check if the battle is finished based on the result."""
        return self.result is not None


    def calculate_damage(self, raw, defender):
        """Calculate the final damage after applying defense, randomness, and critical hits."""

        is_crit = False

        # Apply defense
        damage = max(1, int(raw - defender.defense * DAMAGE_BASE))

        # Apply random factor
        damage += random.randint(0, DAMAGE_RANDOM)

        # Check for critical hit
        if random.random() < CRIT_CHANCE:
            damage *= CRIT_MULTIPLIER
            is_crit = True

        return (damage, is_crit)
