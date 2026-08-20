# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Global constants and game balance configuration.

Holds: the hero and enemy stat templates, the skill definitions, potions,
the damage formula, fleeing, enemy AI weights and battle result states.
Phase 2 will add window/FPS/color constants for pygame.
"""

## Battle configuration
HERO_NAME     = "Hero"
ENEMY_NAME    = "Dark Wisp"

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
COLOR_ACCENT    = (240, 200, 80)    # highlight for the selected menu option

# Colors for the placeholder characters
COLOR_HERO      = (90, 140, 210)    # bluish knight
COLOR_ENEMY     = (200, 90, 90)     # reddish

# Colors for spells
COLOR_FIREBALL    = (255, 100, 0)     # orange
COLOR_SHADOW_BOLT = (128, 0, 128)     # purple

# Fonts
FONT_NAME          = "Arial"  # pygame will fall back if missing
FONT_TITLE_SIZE    = 48
FONT_MENU_SIZE     = 28
FONT_LOG_SIZE      = 20
FONT_HUD_SIZE      = 18
FONT_FLOAT_SIZE    = 26   # damage numbers
FONT_CRIT_SIZE     = 36   # critical hit numbers (bigger)

# Layout (positions in pixels)
HERO_X    = 590
HERO_Y    = 360
ENEMY_X   = 400
ENEMY_Y   = 180
HERO_SCALE  = 1.1
ENEMY_SCALE = 0.95     # smaller => further away
PROJ_RADIUS = 10       # radius of the projectile (spell)

# Hero status card (fixed top-right, enemy info hidden for tension)
CARD_WIDTH  = 150
CARD_HEIGHT = 54
HERO_CARD_RECT = (SCREEN_WIDTH - CARD_WIDTH - 20, 20, CARD_WIDTH, CARD_HEIGHT)

# Bar dimensions
BAR_WIDTH  = 80   # width of the HP/MP bars
BAR_HEIGHT = 12   # height of the HP/MP bars

# Battle menu and log
MENU_RECT = (40, 450, 300, 180)    # (x, y, width, height) menu panel
LOG_RECT  = (360, 450, 560, 180)   # (x, y, width, height) battle log panel

# Animation durations (seconds)
LUNGE_DURATION     = 0.35   # attacker travels to the target
FLASH_DURATION     = 0.15   # impact flash on the defender
RECOIL_DURATION    = 0.15   # defender knocked back
FLOAT_DURATION     = 0.80   # damage number rising and fading
FLY_DURATION       = 0.40   # projectile (spell) travel time

# Distances
LUNGE_GAP          = 30     # px the attacker stops before the target
RECOIL_DISTANCE    = 20     # px the defender is knocked back
RETURN_JUMP_HEIGHT = 50     # px peak of the attacker's backward hop on the return
LUNGE_SCALE_DEPTH  = 0.3    # how much apparent scale changes as the attacker approaches

# Impact flash
FLASH_RADIUS       = 40
FLASH_COLOR        = (255, 255, 200)

# Floating number colors by type
COLOR_DAMAGE       = (255, 230, 80)    # yellow: normal damage
COLOR_CRIT         = (255, 80, 80)     # red: critical hit
COLOR_HEAL         = (120, 230, 120)   # green: heal / potion
COLOR_GRAY         = (225, 225, 225)   # whitish: fails / flee
COLOR_GUARD        = (120, 180, 255)   # light blue: guard

# Floating number rise speed (px per second)
FLOAT_SPEED        = 40

# Float text stays fully opaque for the first 50% of its duration, then fades out
FLOAT_FADE_START   = 0.5

# Assets
BATTLE_BACKGROUNDS = [
    "game/assets/backgrounds/rpg_battle_background_castle_02.png",
    "game/assets/backgrounds/rpg_battle_background_cave_02.png",
    "game/assets/backgrounds/rpg_battle_background_forest_02.png",
    "game/assets/backgrounds/rpg_battle_background_port_02.png"
]

HERO_SPRITES = [
    "game/assets/sprites/hero/hero_01.png",
    "game/assets/sprites/hero/hero_02.png",
    "game/assets/sprites/hero/hero_03.png",
    "game/assets/sprites/hero/hero_04.png",
    "game/assets/sprites/hero/hero_05.png",
    "game/assets/sprites/hero/hero_06.png",
    "game/assets/sprites/hero/hero_07.png",
    "game/assets/sprites/hero/hero_08.png"
]

ENEMY_SPRITES = [
    "game/assets/sprites/enemy/enemy_01.png",
    "game/assets/sprites/enemy/enemy_02.png",
    "game/assets/sprites/enemy/enemy_03.png",
    "game/assets/sprites/enemy/enemy_04.png",
    "game/assets/sprites/enemy/enemy_05.png"
]

# Hero and enemy names
HERO_NAMES = {
    "game/assets/sprites/hero/hero_01.png": "Bryan",
    "game/assets/sprites/hero/hero_02.png": "Matt",
    "game/assets/sprites/hero/hero_03.png": "Sarah",
    "game/assets/sprites/hero/hero_04.png": "Lucy",
    "game/assets/sprites/hero/hero_05.png": "Jane",
    "game/assets/sprites/hero/hero_06.png": "Roberto",
    "game/assets/sprites/hero/hero_07.png": "Jennifer",
    "game/assets/sprites/hero/hero_08.png": "Felix"
}

ENEMY_NAMES = {
    "game/assets/sprites/enemy/enemy_01.png": "Dark Wisp",
    "game/assets/sprites/enemy/enemy_02.png": "Lord Malice",
    "game/assets/sprites/enemy/enemy_03.png": "Dark Mage",
    "game/assets/sprites/enemy/enemy_04.png": "Turtle Dragon",
    "game/assets/sprites/enemy/enemy_05.png": "Satan"
}
