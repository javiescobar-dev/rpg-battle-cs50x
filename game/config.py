# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Global constants and game balance configuration.

Holds: the hero and enemy stat templates, the skill definitions, potions,
the damage formula, fleeing, enemy AI weights and battle result states.
Phase 2 will add window/FPS/color constants for pygame.
"""

## Battle configuration
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


## User interface configuration (pygame)
# Window and FPS settings
SCREEN_WIDTH     = 960
SCREEN_HEIGHT    = 640
FPS              = 60

# Colors (RGB)
COLOR_BG        = (20, 20, 30)      # dark blue-grey background
COLOR_TEXT      = (230, 230, 230)   # light grey text
COLOR_HP_BAR    = (70, 200, 70)     # green
COLOR_MP_BAR    = (70, 130, 220)    # blue
COLOR_BAR_BG    = (50, 50, 60)      # empty part of a bar
COLOR_BORDER    = (230, 230, 230)   # bar and panel borders

# Colors for the placeholder characters
COLOR_HERO      = (90, 140, 210)    # bluish knight
COLOR_ENEMY     = (200, 90, 90)     # reddish

# Fonts
FONT_NAME          = "Arial"  # pygame will fall back if missing
FONT_TITLE_SIZE    = 48
FONT_MENU_SIZE     = 28
FONT_LOG_SIZE      = 20
FONT_HUD_SIZE      = 18

# Layout (positions in pixels)
ARENA_Y      = 260   # vertical center of the fighters (height of characters positions)
HERO_X       = 260   # hero position
ENEMY_X      = 700   # enemy position
# Battle menu and log
MENU_RECT = (40, 450, 300, 180)    # (x, y, width, height) menu panel
LOG_RECT  = (360, 450, 560, 180)   # (x, y, width, height) battle log panel

# Bar dimensions
BAR_WIDTH  = 80   # width of the HP/MP bars
BAR_HEIGHT = 12   # height of the HP/MP bars

# Animation durations (seconds)
LUNGE_DURATION     = 0.25   # attacker moves forward
FLASH_DURATION     = 0.15   # impact flash on the defender
RECOIL_DURATION    = 0.15   # defender knocked back
FLOAT_DURATION     = 0.80   # damage number rising and fading
