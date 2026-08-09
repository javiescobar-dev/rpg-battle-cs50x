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


    def deal_damage(self, attacker, defender, raw_damage, action):
        """Deal damage from attacker to defender and log the action."""

        # get the final damage and whether it was a critical hit
        damage, is_crit = self.calculate_damage(raw_damage, defender)

        # apply the damage to the defender
        was_guarding = defender.guard  # check if the defender was guarding
        damage_dealt = defender.take_damage(damage)  # apply the damage and get the actual damage taken (after guard mitigation)

        # log the action in the battle log
        self.log.append({
            "action": action,
            "attacker": attacker,
            "defender": defender,
            "damage": damage_dealt,
            "is_crit": is_crit,
            "was_guarding": was_guarding
        })

        # check if the defender is still alive after taking damage
        if not defender.is_alive:
            # log the defeat in the battle log and set the result of the battle
            self.log.append({ "action": "defeated", "defender": defender })
            if defender is self.enemy:
                self.result = RESULT_VICTORY
            else:
                self.result = RESULT_DEFEAT


    def player_attack(self):
        """Handle the player's attack action."""
        self.deal_damage(self.hero, self.enemy, self.hero.attack, "attack")


    def player_cast_skill(self, skill_name):
        """Handle the player's skill casting action."""

        # cast_skill do the action and return the value (damage, heal amount, or False if not enough mana)
        value = self.hero.cast_skill(skill_name)

        # check if the skill exists and if the hero has enough mana to cast it
        if not value:
            self.log.append({ "action": "mana_fail", "actor": self.hero, "skill": skill_name })
            return False  # Skill casting failed

        if skill_name == "spell":
            raw_damage = value  # is attack * multiplier
            self.deal_damage(self.hero, self.enemy, raw_damage, "spell")
        elif skill_name == "guard":
            # hero guard is set to True in cast_skill, so we just log the action here
            self.log.append({ "action": "guard", "actor": self.hero })
        elif skill_name == "heal":
            heal_amount = value  # is the amount healed
            self.log.append({ "action": "heal", "actor": self.hero, "amount": heal_amount })

        return True  # Skill casting succeeded


    def player_use_potion(self):
        """Handle the player's potion usage action."""

        value = self.hero.use_potion() # return POTION_AMOUNT if potion was used, or False if no potions left
        if value:
            self.log.append({ "action": "potion", "actor": self.hero, "amount": value })
        else:
            self.log.append({ "action": "potion_fail", "actor": self.hero })


    def player_flee(self):
        """Handle the player's attempt to flee from battle."""

        # calculate flee chance based on speed difference
        speed_diff = self.hero.speed - self.enemy.speed
        chance = FLEE_BASE + (speed_diff * FLEE_SPEED_WEIGHT)
        flee_chance = max(FLEE_MIN, min(FLEE_MAX, chance))  # clamp between min and max

        if random.random() < flee_chance:
            self.log.append({ "action": "flee_success", "actor": self.hero })
            self.result = RESULT_FLED
            return True  # Flee successful
        else:
            self.log.append({ "action": "flee_fail", "actor": self.hero })
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
            self.deal_damage(self.enemy, self.hero, raw_damage, "attack")
        elif action == "spell":
            self.enemy.spend_mana(SKILLS["spell"]["cost"])  # spend mana for the spell
            raw_damage = self.enemy.attack * SKILLS["spell"]["multiplier"]
            self.deal_damage(self.enemy, self.hero, raw_damage, "spell")
        elif action == "guard":
            self.enemy.guard = True  # Set guard state
            self.log.append({ "action": "guard", "actor": self.enemy })


def format_event(event):
    """Format a battle event into a human-readable string for logging."""

    action = event.get("action")
    actor = event.get("actor")
    attacker = event.get("attacker")
    defender = event.get("defender")
    damage = event.get("damage")
    crit = " (CRITICAL HIT!)" if event.get("is_crit") else ""  # only show crit message if it was a critical hit
    amount = event.get("amount", 0)
    skill = event.get("skill")

    log_message = ""
    if action == "attack":
        log_message = f"{attacker.name} attacks {defender.name} for {damage} damage{crit}."
    elif action == "spell":
        log_message = f"{attacker.name} casts {attacker.spell_name} on {defender.name} for {damage} damage{crit}."
    elif action == "guard":
        log_message = f"{actor.name} is guarding and will mitigate damage of the next attack."
    elif action == "heal":
        log_message = f"{actor.name} casts Heal and restores {amount} HP."
    elif action == "potion":
        log_message = f"{actor.name} uses a potion and restores {amount} HP."
    elif action == "mana_fail":
        log_message = f"{actor.name} tried to cast {skill}, but failed (not enough mana)."
    elif action == "potion_fail":
        log_message = f"{actor.name} tried to use a potion, but has none left."
    elif action == "flee_success":
        log_message = f"{actor.name} successfully fled from battle!"
    elif action == "flee_fail":
        log_message = f"{actor.name} failed to flee from battle."
    elif action == "defeated":
        log_message = f"{defender.name} has been defeated!"
    else:
        log_message = str(event)  # fallback to string representation of the event if action is unrecognized

    return log_message
