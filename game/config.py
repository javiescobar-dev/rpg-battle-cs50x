# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Global constants and game balance configuration."""

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
COLOR_BG             = (20, 20, 30)      # dark blue-grey background
COLOR_TEXT           = (230, 230, 230)   # light grey text
COLOR_TEXT_MAIN      = (78, 78, 78)      # light grey text for Main menu
COLOR_TEXT_TITLE     = (33, 33, 33)      # black text for Title
COLOR_HP_BAR         = (70, 200, 70)     # green
COLOR_MP_BAR         = (70, 130, 220)    # blue
COLOR_BAR_BG         = (50, 50, 60)      # empty part of a bar
COLOR_BORDER         = (230, 230, 230)   # bar and panel borders
COLOR_ACCENT         = (240, 200, 80)    # highlight for the selected menu option
COLOR_ACCENT_MAIN    = (80, 200, 240)    # highlight for the selected menu option (Main menu)
COLOR_TEXT_FOOTER    = (80, 80, 80)      # medium grey

# Colors for spells
COLOR_FIREBALL    = (255, 100, 0)     # orange
COLOR_SHADOW_BOLT = (128, 0, 128)     # purple

# Spell core colors (bright center of the projectile)
COLOR_FIREBALL_CORE    = (255, 240, 100)   # bright yellow
COLOR_SHADOW_BOLT_CORE = (200, 50, 255)    # bright purple

# Spell particle color palettes (3 colors each, chosen randomly per particle)
FIREBALL_PARTICLE_COLORS = [
    (255, 180, 50),   # bright yellow-orange
    (255, 100, 0),    # orange
    (255, 50, 0),     # red-orange
]
SHADOW_BOLT_PARTICLE_COLORS = [
    (180, 0, 255),    # bright purple
    (100, 0, 180),    # dark purple
    (50, 200, 50),    # green spark
]

# Spell projectile effects
TRAIL_LENGTH        = 8      # trail length (previous position)
TRAIL_MIN_RADIUS    = 2      # smallest trail radius
TRAIL_MIN_ALPHA     = 40     # lowest trail alpha
PULSE_AMPLITUDE     = 3      # halo radius oscillation
PULSE_SPEED         = 8      # oscillation speed (sin)

# Impact explosion
IMPACT_RING_COUNT         = 2      # expanding rings on impact
IMPACT_RING_SPEED         = 120    # px/s expansion radius
IMPACT_RING_MAX_RADIUS    = 35     # maximum ring radius
IMPACT_RING_WIDTH         = 3      # ring border width

# Particles
PARTICLE_INITIAL_BURST = 8      # particles spawned at cast (initial burst)
PARTICLES_PER_FRAME    = 1      # particles spawned per frame during flight
PARTICLE_LIFE          = 0.3    # particle duration (s)
PARTICLE_SPEED         = 80     # particle speed (px/s)
PARTICLE_MIN_RADIUS    = 1      # minimum particle radius
IMPACT_PARTICLE_COUNT  = 12     # particles burst on impact
IMPACT_PARTICLE_SPEED  = 150    # impact particle speed (px/s)
IMPACT_PARTICLE_LIFE   = 0.4    # impact particle duration (s)

# Fonts
FONT_NAME          = "Arial"  # pygame will fall back if missing
FONT_NAME_TITLE    = "game/assets/fonts/finalf.ttf"
FONT_TITLE_SIZE    = 64
FONT_MENU_SIZE     = 28
FONT_LOG_SIZE      = 20
FONT_HUD_SIZE      = 18
FONT_FLOAT_SIZE    = 26   # damage numbers
FONT_CRIT_SIZE     = 36   # critical hit numbers (bigger)
FONT_END_SIZE      = 64   # end screen text
FONT_FOOTER_SIZE = 14

# Panel styling
PANEL_ALPHA          = 140   # alpha for semi-transparent panels
PANEL_BORDER         = (0, 0, 0)  # black border for panels
PANEL_BORDER_MAIN    = (255, 255, 255)  # border for the main panel

# Layout (positions in pixels)
HERO_X          = 590
HERO_Y          = 360
ENEMY_X         = 400
ENEMY_Y         = 180
HERO_SCALE      = 1.1
ENEMY_SCALE     = 0.95     # smaller => further away
PROJ_RADIUS     = 10       # radius of the projectile (spell)

# Hero status card (fixed top-right, enemy info hidden for tension)
CARD_WIDTH  = 240
CARD_HEIGHT = 64
HERO_CARD_RECT = (SCREEN_WIDTH - CARD_WIDTH - 20, 20, CARD_WIDTH, CARD_HEIGHT)

# Bar dimensions
BAR_WIDTH  = 80   # width of the HP/MP bars
BAR_HEIGHT = 12   # height of the HP/MP bars

# Battle menu and log
MENU_RECT = (40, 450, 300, 180)    # (x, y, width, height) menu panel
LOG_RECT  = (360, 450, 560, 180)   # (x, y, width, height) battle log panel

# Dark overlay alphas for different screens (0–255)
OVERLAY_END    = 140

# Fade screen effect duration
FADE_DURATION = 0.5

# Animation durations (seconds)
LUNGE_DURATION     = 0.35   # attacker travels to the target
FLASH_DURATION     = 0.15   # impact flash on the defender
RECOIL_DURATION    = 0.15   # defender knocked back
FLOAT_DURATION     = 0.80   # damage number rising and fading
FLY_DURATION       = 0.40   # projectile (spell) travel time
CHOSE_DELAY        = 0.65   # delay between confirming and executing an action

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
# Title screen background
TITLE_BG_PATH = "game/assets/backgrounds/rpg_battle_background_title.png"

# Battle backgrounds
BATTLE_BACKGROUNDS = [
    "game/assets/backgrounds/rpg_battle_background_castle.png",
    "game/assets/backgrounds/rpg_battle_background_cave.png",
    "game/assets/backgrounds/rpg_battle_background_forest.png",
    "game/assets/backgrounds/rpg_battle_background_port.png"
]

# Hero and enemy sprites and names
HEROES = [
    ("game/assets/sprites/hero/hero_01.png", "Bryan"),
    ("game/assets/sprites/hero/hero_02.png", "Matt"),
    ("game/assets/sprites/hero/hero_03.png", "Sarah"),
    ("game/assets/sprites/hero/hero_04.png", "Lucy"),
    ("game/assets/sprites/hero/hero_05.png", "Jane"),
    ("game/assets/sprites/hero/hero_06.png", "Roberto"),
    ("game/assets/sprites/hero/hero_07.png", "Jennifer"),
    ("game/assets/sprites/hero/hero_08.png", "Felix")
]

ENEMIES = [
    ("game/assets/sprites/enemy/enemy_01.png", "Dark Wisp"),
    ("game/assets/sprites/enemy/enemy_02.png", "Lord Malice"),
    ("game/assets/sprites/enemy/enemy_03.png", "Dark Mage"),
    ("game/assets/sprites/enemy/enemy_04.png", "Turtle Dragon"),
    ("game/assets/sprites/enemy/enemy_05.png", "Satan")
]

# Sound effects
SFX_DIR = "game/assets/sfx"
SFX = {
    "attack":       f"{SFX_DIR}/attack.wav",
    "lunge":        f"{SFX_DIR}/lunge.wav",
    "cast_spell":   f"{SFX_DIR}/cast_spell.wav",
    "spell_hit":    f"{SFX_DIR}/spell_hit.wav",
    "guard":        f"{SFX_DIR}/guard.wav",
    "heal":         f"{SFX_DIR}/heal.wav",
    "potion":       f"{SFX_DIR}/potion.wav",
    "mana_fail":    f"{SFX_DIR}/fail.wav",
    "potion_fail":  f"{SFX_DIR}/fail.wav",
    "flee_success": f"{SFX_DIR}/flee.wav",
    "flee_fail":    f"{SFX_DIR}/flee.wav",
    "defeated":     f"{SFX_DIR}/defeated.wav",
    "victory":      f"{SFX_DIR}/victory.wav",
    "defeat":       f"{SFX_DIR}/defeat.mp3",
    "cursor":       f"{SFX_DIR}/cursor.wav",
    "confirm":      f"{SFX_DIR}/confirm.wav",
}
