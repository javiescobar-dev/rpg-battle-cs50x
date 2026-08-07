# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Global constants and game balance configuration.

Holds: the hero and enemy stat templates, the skill definitions, potions,
the damage formula, fleeing, enemy AI weights and battle result states.
Phase 2 will add window/FPS/color constants for pygame.
"""

# Stats base
HERO_HP          = 100
HERO_MP          = 30
HERO_ATTACK      = 15
HERO_DEFENSE     = 10
HERO_SPEED       = 12

ENEMY_HP         = 80
ENEMY_MP         = 20
ENEMY_ATTACK     = 13
ENEMY_DEFENSE    = 8
ENEMY_SPEED      = 10

# Skills
## costs
SPELL_COST             = 8
GUARD_COST             = 4
HEAL_COST              = 6
## multipliers
SPELL_MULTIPLIER       = 1.8    # multiplier for damage formula
GUARD_MITIGATION       = 0.5    # percentage of damage mitigated
HEAL_AMOUNT            = 30     # amount of HP restored
## skill definitions
SKILLS = {
    "spell": {"cost": SPELL_COST, "multiplier": SPELL_MULTIPLIER},
    "guard": {"cost": GUARD_COST, "mitigation": GUARD_MITIGATION},
    "heal":  {"cost": HEAL_COST,  "amount": HEAL_AMOUNT},
}
HERO_SPELL_NAME = "Fireball"
ENEMY_SPELL_NAME = "Shadow Bolt"

# Items
POTION_AMOUNT     = 25    # amount of HP restored
POTION_START      = 3     # starting number of potions

# Damage formula
DAMAGE_BASE         = 0.5    # base damage multiplier (defense reduces damage)
DAMAGE_RANDOM       = 5      # random damage range
# Critical hits
CRIT_CHANCE         = 0.1    # 10% chance of a critical hit
CRIT_MULTIPLIER     = 1.5    # damage multiplied on a crit

# Fleeing
FLEE_BASE            = 0.5     # base flee chance
FLEE_SPEED_WEIGHT    = 0.05    # weight of speed difference in flee chance
FLEE_MIN             = 0.25    # minimum flee chance
FLEE_MAX             = 0.90    # maximum flee chance

# Enemy AI weights (sum = 1.0 = 100%)
ENEMY_ATTACK_WEIGHT      = 0.5     # weight for choosing attack
ENEMY_SPELL_WEIGHT       = 0.3     # weight for choosing spell
ENEMY_GUARD_WEIGHT       = 0.2     # weight for choosing guard

# Battle result states
RESULT_VICTORY    = "victory"
RESULT_DEFEAT     = "defeat"
RESULT_FLED       = "fled"
