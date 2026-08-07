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


    def calculate_damage(self, raw_damage, defender):
        """Calculate the final damage after applying defense, randomness, and critical hits."""

        is_crit = False

        # Apply defense
        damage = max(1, int(raw_damage - defender.defense * DAMAGE_BASE))

        # Apply random factor
        damage += random.randint(0, DAMAGE_RANDOM)

        # Check for critical hit
        if random.random() < CRIT_CHANCE:
            damage = int(damage * CRIT_MULTIPLIER)
            is_crit = True

        return (damage, is_crit)


    def deal_damage(self, attacker, defender, raw_damage, action_text):
        """Deal damage from attacker to defender and log the action."""

        # get the final damage and whether it was a critical hit
        damage, is_crit = self.calculate_damage(raw_damage, defender)

        # apply the damage to the defender
        defender.take_damage(damage)
        crit_text = " (CRITICAL HIT!)" if is_crit else ""
        self.log.append(f"{attacker.name} {action_text} for {damage} damage{crit_text}.")

        # check if the defender is still alive after taking damage
        if not defender.is_alive:
            self.log.append(f"{defender.name} has been defeated!")
            if defender is self.enemy:
                self.result = RESULT_VICTORY
            else:
                self.result = RESULT_DEFEAT


    def player_attack(self):
        """Handle the player's attack action."""
        raw_damage = self.hero.attack
        action_text = f"attacks {self.enemy.name}"
        self.deal_damage(self.hero, self.enemy, raw_damage, action_text)


    def player_cast_skill(self, skill_name):
        """Handle the player's skill casting action."""

        # cast_skill do the action and return the value (damage, heal amount, or False if not enough mana)
        value = self.hero.cast_skill(skill_name)

        # check if the skill exists and if the hero has enough mana to cast it
        if not value:
            self.log.append(f"{self.hero.name} tried to cast {skill_name}, but failed (not enough mana).")
            return False  # Skill casting failed

        if skill_name == "spell":
            raw_damage = value  # is attack * multiplier
            action_text = f"casts {self.hero.spell_name} on {self.enemy.name}"
            self.deal_damage(self.hero, self.enemy, raw_damage, action_text)
        elif skill_name == "guard":
            # hero guard is set to True in cast_skill, so we just log the action here
            self.log.append(f"{self.hero.name} is guarding and will mitigate damage next turn.")
        elif skill_name == "heal":
            heal_amount = value  # is the amount healed
            self.log.append(f"{self.hero.name} casts Heal and restores {heal_amount} HP.")

        return True  # Skill casting succeeded
