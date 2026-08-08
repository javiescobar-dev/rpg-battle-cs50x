# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Console entry point for Phase 1.

Runs a playable turn-based battle in the terminal: main menu, battle UI with
a hybrid log (only new messages plus an always-visible status line), score
recording and statistics. Will be rewritten in phase 2 to launch a pygame
window.
"""

from game.battle import Battle
from game.config import RESULT_VICTORY, RESULT_DEFEAT, RESULT_FLED
from game.entities import make_hero, make_enemy
from game.score import add_result, summary

def print_status(battle):
    """Print the current status of the hero and enemy, including HP and MP."""
    hero = battle.hero
    enemy = battle.enemy
    print(f"\n{hero.name}: HP {hero.hp}/{hero.max_hp}, MP {hero.mp}/{hero.max_mp}, Potions {hero.potions}")
    print(f"{enemy.name}: HP {enemy.hp}/{enemy.max_hp}, MP {enemy.mp}/{enemy.max_mp}\n")


def print_menu():
    """Print the action menu for the player."""
    print("\n[1] Attack  [2] Skill  [3] Potion  [4] Flee")


def choose_skill(hero):
    """Prompt the player to choose a skill and return the corresponding action."""
    print(f"[1] {hero.spell_name}  [2] Guard  [3] Heal")

    # get the player's choice and map it to the corresponding action
    choice = input("> ").strip()  # strip whitespace from the input
    mapping = {
        "1": "spell",
        "2": "guard",
        "3": "heal"
    }

    # Return the corresponding action or None if invalid
    return mapping.get(choice)
