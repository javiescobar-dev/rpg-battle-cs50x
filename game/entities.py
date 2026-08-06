# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Combat entities: a base Character class plus the Hero and Enemy subclasses.

Holds: the Character base class, the Hero/Enemy subclasses, and the
factory helpers (make_hero / make_enemy) used to build combatants.
"""

import random
from game.config import (
    SKILLS, POTION_AMOUNT, POTION_START, GUARD_MITIGATION,
    HERO_HP, HERO_MP, HERO_ATTACK, HERO_DEFENSE, HERO_SPEED, HERO_SPELL_NAME,
    ENEMY_HP, ENEMY_MP, ENEMY_ATTACK, ENEMY_DEFENSE, ENEMY_SPEED, ENEMY_SPELL_NAME,
    ENEMY_ATTACK_WEIGHT, ENEMY_SPELL_WEIGHT, ENEMY_GUARD_WEIGHT,
)

class Character:
    """Base combatant: common stats and self-mutations only."""

    def __init__(self, name, hp, mp, attack, defense, speed, spell_name="spell"):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_mp = mp
        self.mp = mp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.spell_name = spell_name
        self.guard = False


    # use decorator @property to make is_alive a read-only property, like a getter method,
    # so that it can be accessed as an attribute without parentheses.
    @property
    def is_alive(self):
        return self.hp > 0


    # Method to take damage, reducing HP and applying guard mitigation if active
    def take_damage(self, amount):
        if self.guard:
            amount = int(amount * (1 - GUARD_MITIGATION))  # Apply guard mitigation
            self.guard = False  # Reset guard state after taking damage
        self.hp = max(0, self.hp - amount)


    # Method to heal, increasing HP but not exceeding max HP
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)


    # Method to spend mana, reducing MP if enough is available
    def spend_mana(self, cost):
        if self.mp >= cost:
            self.mp -= cost
            return True
        return False


class Hero(Character):
    """The player-controlled hero."""

    def __init__(self, name, hp, mp, attack, defense, speed, spell_name="spell"):
        super().__init__(name, hp, mp, attack, defense, speed, spell_name)
        self.potions = POTION_START


    # Method to cast a skill, checking for mana and applying effects
    def cast_skill(self, skill_name):
        data = SKILLS.get(skill_name)

        # check if the skill exists
        if not data:
            return False  # Skill does not exist

        # check if the hero has enough mana to cast the skill
        if not self.spend_mana(data["cost"]):
            return False  # Not enough mana

        # check if the skill is "spell", "guard", or "heal" and apply the corresponding effect
        if skill_name == "spell":
            return self.attack * data["multiplier"]  # Return the damage multiplier for spell
        elif skill_name == "guard":
            self.guard = True  # Set guard state
            return True  # Guard activated, no damage dealt
        elif skill_name == "heal":
            self.heal(data["amount"])  # Heal the hero
            return data["amount"]  # Heal activated


    # Method to use a potion, restoring HP and reducing the potion count
    def use_potion(self):
        if self.potions > 0:
            self.heal(POTION_AMOUNT)
            self.potions -= 1
            return POTION_AMOUNT
        return False  # No potions left


class Enemy(Character):
    """AI-controlled enemy."""

    def __init__(self, name, hp, mp, attack, defense, speed, spell_name="spell"):
        super().__init__(name, hp, mp, attack, defense, speed, spell_name)


    # Method to choose the enemy's action based on weighted probabilities
    def choose_action(self):
        actions = ["attack", "spell", "guard"]
        weights = [ENEMY_ATTACK_WEIGHT, ENEMY_SPELL_WEIGHT, ENEMY_GUARD_WEIGHT]
        action = random.choices(actions, weights=weights)[0]
        if action in ("spell", "guard") and self.mp < SKILLS[self.spell_name]["cost"]:
            action = "attack"  # Fallback to attack if not enough mana
        return action
