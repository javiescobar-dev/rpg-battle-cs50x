# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Turn-based battle engine. Pure logic with no rendering.

The Battle class orchestrates player and enemy turns: the damage formula
(with defense, randomness and critical hits), skill casting, guard,
potions, fleeing, and the end conditions (victory / defeat / fled).
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


    # use decorator @property to make is_finished a read-only property, like a getter method,
    # so that it can be accessed as an attribute without parentheses.
    @property
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
        damage_dealt = defender.take_damage(damage)  # apply the damage and get the actual damage taken (after guard mitigation)
        crit_text = " (CRITICAL HIT!)" if is_crit else ""
        self.log.append(f"{attacker.name} {action_text} for {damage_dealt} damage{crit_text}.")

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


    def player_use_potion(self):
        """Handle the player's potion usage action."""

        value = self.hero.use_potion() # return POTION_AMOUNT if potion was used, or False if no potions left
        if value:
            self.log.append(f"{self.hero.name} uses a potion and restores {value} HP.")
        else:
            self.log.append(f"{self.hero.name} tried to use a potion, but has none left.")


    def player_flee(self):
        """Handle the player's attempt to flee from battle."""

        # calculate flee chance based on speed difference
        speed_diff = self.hero.speed - self.enemy.speed
        chance = FLEE_BASE + (speed_diff * FLEE_SPEED_WEIGHT)
        flee_chance = max(FLEE_MIN, min(FLEE_MAX, chance))  # clamp between min and max

        if random.random() < flee_chance:
            self.log.append(f"{self.hero.name} successfully fled from battle!")
            self.result = RESULT_FLED
            return True  # Flee successful
        else:
            self.log.append(f"{self.hero.name} failed to flee from battle.")
            return False  # Flee failed


    def player_turn(self, action, skill_name=None):
        """Handle the player's turn based on the chosen action."""

        if self.is_finished:  # Only allow actions if the battle is not finished
            return

        if action == "attack":
            self.player_attack()
        elif action == "skill" and skill_name:
            self.player_cast_skill(skill_name)
        elif action == "potion":
            self.player_use_potion()
        elif action == "flee":
            self.player_flee()
        else:
            self.log.append(f"{self.hero.name} did nothing this turn.")

        # increment the turn counter after the player's action
        self.turns += 1

        # set turn to enemy if the battle is not finished
        if not self.is_finished:
            self.enemy_turn()


    def enemy_turn(self):
        """Handle the enemy's turn, choosing an action based on weighted probabilities."""

        # choose an action based on weights
        action = self.enemy.choose_action()  # returns "attack", "spell", or "guard"

        if action == "attack":
            raw_damage = self.enemy.attack
            action_text = f"attacks {self.hero.name}"
            self.deal_damage(self.enemy, self.hero, raw_damage, action_text)
        elif action == "spell":
            self.enemy.spend_mana(SKILLS["spell"]["cost"])  # spend mana for the spell
            raw_damage = self.enemy.attack * SKILLS["spell"]["multiplier"]
            action_text = f"casts {self.enemy.spell_name} on {self.hero.name}"
            self.deal_damage(self.enemy, self.hero, raw_damage, action_text)
        elif action == "guard":
            self.enemy.guard = True  # Set guard state
            self.log.append(f"{self.enemy.name} is guarding and will mitigate damage of the next attack.")
