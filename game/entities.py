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

    @property
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def spend_mana(self, cost):
        if self.mp >= cost:
            self.mp -= cost
            return True
        return False
