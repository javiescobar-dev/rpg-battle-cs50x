# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Pygame entry point: MENU / STATS / BATTLE / ANIM / END state machine."""


import pygame
from game.battle import Battle
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT, FONT_NAME, FONT_TITLE_SIZE, FONT_MENU_SIZE,
    HERO_X, ENEMY_X, ARENA_Y, COLOR_HERO, COLOR_ENEMY, LOG_RECT, MENU_RECT
)
from game.entities import make_hero, make_enemy
from game.ui import CharacterSprite, LogPanel
from game.ui import Menu


# states of the game
MENU, STATS, BATTLE, ANIM, END = "MENU", "STATS", "BATTLE", "ANIM", "END"


def make_main_menu(font):
    """Create the main menu widget, centered on screen."""
    width = 300
    height = 3 * (font.get_height() + 8) + 16  # 3 options + padding
    # create rect for menu, centered horizontally and with a little offset vertically
    rect = ((SCREEN_WIDTH - width) // 2, (SCREEN_HEIGHT - height) // 2 + 60, width, height)
    # create menu widget
    return Menu(rect, ["Play", "Statistics", "Quit"], font)


def draw_menu_screen(screen, title_font, menu):
    """Draw the title and the main menu."""
    # render the title
    title = title_font.render("RPG Battle", True, COLOR_TEXT)
    # draw the title
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 90))
    # draw the menu
    menu.draw(screen)


def draw_placeholder(screen, title_font, text):
    """Temporary screen for states not implemented yet."""
    # render text
    label = title_font.render(text, True, COLOR_TEXT)
    # draw text on screen, centered horizontally and vertically
    screen.blit(label, ((SCREEN_WIDTH - label.get_width()) // 2, (SCREEN_HEIGHT - label.get_height()) // 2))


def main():
    """Run the pygame window main loop."""

    # ----------------------------------------------------------------------
    # Pygame Initialization
    # ----------------------------------------------------------------------
    # initialize pygame (events, video, audio, etc.)
    pygame.init()

    # set up the display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # set the window title
    pygame.display.set_caption("RPG Battle")

    # create a clock to manage the frame rate (limit game to 60 FPS and return the time since the last frame in seconds)
    clock = pygame.time.Clock()

    # create fonts for main menu
    font_title = pygame.font.SysFont(FONT_NAME, FONT_TITLE_SIZE)
    font_menu = pygame.font.SysFont(FONT_NAME, FONT_MENU_SIZE)

    # set initial state
    state = MENU

    # create Main Menu
    main_menu = make_main_menu(font_menu)

    # set the running flag to True to enter the main loop
    running = True

    # define the function to handle the selection of an option in the main menu
    def select(index):
        """Run the chosen main-menu option."""
        # use nonlocal to modify the state and running variables
        nonlocal state, running
        if index == 0:          # Play
            state = BATTLE
        elif index == 1:        # Statistics
            state = STATS
        elif index == 2:        # Quit
            running = False

    # method to handle events
    def handle_events():
        """Handle events, including quitting the game."""
        # use nonlocal to modify the state and running variables
        nonlocal state, running
        for event in pygame.event.get():
            # handle quit
            if event.type == pygame.QUIT:
                running = False
            # handle menu events
            elif state == MENU:
                # handle key press events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        main_menu.move_cursor(-1)
                    elif event.key == pygame.K_DOWN:
                        main_menu.move_cursor(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        select(main_menu.cursor)
                    elif event.key == pygame.K_1:
                        select(0)
                    elif event.key == pygame.K_2:
                        select(1)
                    elif event.key == pygame.K_3:
                        select(2)
                # handle mouse motion events
                elif event.type == pygame.MOUSEMOTION:
                    index = main_menu.index_at(event.pos)  # row under mouse
                    if index is not None:                  # if mouse is over an option
                        main_menu.cursor = index           # cursor follows mouse
                # handle mouse click events
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    select(main_menu.handle_click(event.pos))
            # handle states
            elif state in (STATS, BATTLE, ANIM, END):
                # TODO: temporary — any key/click returns to the menu
                if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    state = MENU

    def handle_draw():
        """Handle drawing."""
        # fill the screen with the background color
        screen.fill(COLOR_BG)

        # draw based on state
        if state == MENU:
            draw_menu_screen(screen, font_title, main_menu)
        elif state == BATTLE:
            draw_placeholder(screen, font_title, "Battle - coming soon")
        elif state == STATS:
            draw_placeholder(screen, font_title, "Statistics - coming soon")
        elif state == ANIM:
            draw_placeholder(screen, font_title, "Animation - coming soon")
        elif state == END:
            draw_placeholder(screen, font_title, "End - coming soon")

        # update the display
        pygame.display.flip()

    # ----------------------------------------------------------------------
    # BATTLE
    # ----------------------------------------------------------------------
    # initialize battle variables
    battle = None
    hero_sprite = None
    enemy_sprite = None
    battle_log = None
    battle_menu = None
    menu_level = 0
    pending_events = []

    def start_battle():
        """Start a new battle."""
        nonlocal battle, hero_sprite, enemy_sprite, battle_log, battle_menu, menu_level, pending_events
        # create battle
        battle = Battle(make_hero(), make_enemy())
        # create sprites for hero and enemy
        hero_sprite = CharacterSprite(battle.hero, HERO_X, ARENA_Y, COLOR_HERO)
        enemy_sprite = CharacterSprite(battle.enemy, ENEMY_X, ARENA_Y, COLOR_ENEMY)
        # create battle log
        battle_log = LogPanel(LOG_RECT)
        # create battle menu
        battle_menu = Menu(MENU_RECT, ["Fight", "Item", "Run"], font_menu)
        # set menu level
        menu_level = 0
        # set pending events
        pending_events = []

    def choose_action(index):
        """Select action in the battle menu."""
        # use nonlocal to modify the state and pending_events variables
        nonlocal menu_level
        if menu_level == 0:
            if index == 0:    # Fight
                pass
            elif index == 1:  # Item
                pass
            elif index == 2:  # Run
                pass
        elif menu_level == 1:
            if index == 0:    # Attack
                pass
            elif index == 1:  # Skill
                pass
            elif index == 2:  # Back
                pass
        elif menu_level == 2:
            if index == 0:    # Fireball
                pass
            elif index == 1:  # Guard
                pass
            elif index == 2:  # Heal
                pass
            elif index == 3:  # Back
                pass
        elif menu_level == 3:
            if index == 0:    # Potion
                pass
            elif index == 1:  # Back
                pass

    def resolve_turn(action, skill = None):
        """Resolve the turn"""
        # get previous number of events
        prev = len(battle.log)
        # player turn
        battle.player_turn(action, skill)
        # get new events
        pending_events = battle.log[prev:]
        # set state ANIM
        state = ANIM

    def update():
        """Update game state."""
        pass

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------
    while running:
        # update the clock
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        # handle events, including quitting the game
        handle_events()

        # update (empty for now; ANIM will use it)
        update()

        # handle drawing
        handle_draw()

    # quit pygame when the main loop ends
    pygame.quit()


# Draw Helpers
def draw_battle_screen(screen, font, menu):
    """Draw battle screen"""
    pass


def draw_end_screen(screen, font, result):
    """Draw end screen"""
    pass


def draw_stats_screen(screen, font, stats):
    """Draw stats screen"""
    pass


if __name__ == "__main__":
    main()
