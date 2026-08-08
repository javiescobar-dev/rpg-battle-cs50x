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


def play_battle():
    """Main loop for playing a battle, handling user input and battle resolution."""

    # create a new battle instance with a hero and an enemy
    battle = Battle(make_hero(), make_enemy())

    # loop until the battle is finished
    while not battle.is_finished:
        print_status(battle)  # display the current status of the battle
        print_menu()          # display the action menu

        # get the player's action choice
        choice = input("> ").strip()

        # store the previous log length to determine if new messages were added
        prev_log_length = len(battle.log)

        # handle the player's action choice
        if choice == "1":
            battle.player_turn("attack")
        elif choice == "2":
            skill = choose_skill(battle.hero)
            if skill:
                battle.player_turn("skill", skill)
            else:
                print("Invalid skill choice.")
                continue  # skip to the next iteration to re-prompt
        elif choice == "3":
            battle.player_turn("potion")
        elif choice == "4":
            battle.player_turn("flee")
        else:
            print("Invalid action.")
            continue  # skip to the next iteration to re-prompt

        # iterate over the new log messages and print them to the console
        for line in battle.log[prev_log_length:]:  # print only new log messages
            print(line)

        # check battle result and print the outcome if finished
        if battle.is_finished:
            if battle.result == RESULT_VICTORY:
                print(f"\nVictory! {battle.hero.name} has defeated {battle.enemy.name}!")
            elif battle.result == RESULT_DEFEAT:
                print(f"\nDefeat! {battle.hero.name} has been defeated by {battle.enemy.name}.")
            elif battle.result == RESULT_FLED:
                print(f"\n{battle.hero.name} has fled from battle against {battle.enemy.name}.")

            # record the battle result in the scores file
            add_result(
                result=battle.result,
                turns=battle.turns,
                hero_hp_left=battle.hero.hp,
                hero_hp_max=battle.hero.max_hp,
                enemy_name=battle.enemy.name
            )

            # display a summary of all battle results
            stats = summary()
            print("\nBattle Summary:")
            print(f"Total Battles: {stats['total_battles']}")
            print(f"Victories: {stats['victories']}")
            print(f"Defeats: {stats['defeats']}")
            print(f"Flees: {stats['flees']}")
            if stats['most_common_enemy']:
                print(f"Most Common Enemy: {stats['most_common_enemy']}")
