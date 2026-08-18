# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Pygame entry point: MENU / STATS / BATTLE / ANIM / END state machine."""

import pygame
from game.battle import Battle, format_event
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT, FONT_NAME, FONT_TITLE_SIZE, FONT_MENU_SIZE,
    HERO_X, ENEMY_X, HERO_Y, ENEMY_Y, COLOR_HERO, COLOR_ENEMY, HERO_SCALE, ENEMY_SCALE, HERO_CARD_RECT,
    LOG_RECT, MENU_RECT, FONT_HUD_SIZE, FONT_LOG_SIZE, RESULT_VICTORY, RESULT_DEFEAT, RESULT_FLED
)
from game.entities import make_hero, make_enemy
from game.ui import CharacterSprite, LogPanel, Menu, EventPlayer, draw_hud, draw_enemy_name
from game.score import add_result, summary
from game.assets import load_character_sprites

# states of the game
MENU, STATS, BATTLE, ANIM, END = "MENU", "STATS", "BATTLE", "ANIM", "END"

# battle menu levels
MAIN_MENU, SKILL_MENU = 0, 1

# battle menu options
BATTLE_OPTIONS = ["Attack", "Skill", "Potion", "Flee"]
SKILL_OPTIONS  = ["Fireball", "Guard", "Heal", "Back"]


# ----------------------------------------------------------------------
# Pygame Widget Helpers
# ----------------------------------------------------------------------
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

    # create fonts for HUD and log
    font_hud = pygame.font.SysFont(FONT_NAME, FONT_HUD_SIZE)
    font_log = pygame.font.SysFont(FONT_NAME, FONT_LOG_SIZE)

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
            start_battle()
            state = BATTLE
        elif index == 1:        # Statistics
            state = STATS
        elif index == 2:        # Quit
            running = False

    # method to handle events
    def handle_events():
        """Handle events, including quitting the game."""
        # use nonlocal to modify the state and running variables
        nonlocal state, running, menu_level
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
            # handle battle menu events
            elif state == BATTLE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        battle_menu.move_cursor(-1)
                    elif event.key == pygame.K_DOWN:
                        battle_menu.move_cursor(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        choose_action(battle_menu.cursor)
                    elif event.key == pygame.K_ESCAPE and menu_level == SKILL_MENU:
                        menu_level = MAIN_MENU
                        battle_menu.options = BATTLE_OPTIONS
                        battle_menu.cursor = 0
                    elif event.key == pygame.K_1:
                        choose_action(0)
                    elif event.key == pygame.K_2:
                        choose_action(1)
                    elif event.key == pygame.K_3:
                        choose_action(2)
                    elif event.key == pygame.K_4:
                        choose_action(3)
                elif event.type == pygame.MOUSEMOTION:
                    index = battle_menu.index_at(event.pos)
                    if index is not None:
                        battle_menu.cursor = index
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    choose_action(battle_menu.handle_click(event.pos))
            # handle states (ANIM is not handled, it is automatic)
            elif state in (STATS, END):
                # TODO: temporary — any key/click returns to the menu
                if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    state = MENU

    def handle_draw():
        """Handle drawing."""
        # use nonlocal to modify the state and other variables
        nonlocal state, hero_sprite, enemy_sprite, battle_log, event_player, battle_menu, font_hud, font_log
        # fill the screen with the background color
        screen.fill(COLOR_BG)

        # draw based on state
        if state == MENU:
            draw_menu_screen(screen, font_title, main_menu)
        elif state in (BATTLE, ANIM):  # draw battle screen (ANIM is not handled, it is automatic, but we still need to draw the battle screen)
            draw_battle_screen(screen, hero_sprite, enemy_sprite, font_hud, battle_log, font_log, battle_menu, show_menu=(state == BATTLE), event_player=event_player)
        elif state == STATS:
            draw_stats_screen(screen, font_title, font_menu, summary())
        elif state == END:
            draw_end_screen(screen, font_title, font_menu, battle, summary())

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
    event_player = None
    battle_menu = None
    menu_level = 0
    pending_events = []

    # Callback function used by the EventPlayer to add formatted events to the battle log
    def log_event(event):
        battle_log.add(format_event(event))

    def start_battle():
        """Start a new battle."""
        nonlocal battle, hero_sprite, enemy_sprite, battle_log, event_player, battle_menu, menu_level, pending_events
        # create battle
        battle = Battle(make_hero(), make_enemy())
        # load animations
        hero_animations = load_character_sprites("game/assets/sprites/hero.png")
        enemy_animations = load_character_sprites("game/assets/sprites/enemy.png")
        # create sprites for hero and enemy
        hero_sprite = CharacterSprite(battle.hero, HERO_X, HERO_Y, COLOR_HERO, HERO_SCALE, hero_animations)
        enemy_sprite = CharacterSprite(battle.enemy, ENEMY_X, ENEMY_Y, COLOR_ENEMY, ENEMY_SCALE, enemy_animations)
        # create battle log
        battle_log = LogPanel(LOG_RECT)
        # create event player
        event_player = EventPlayer(hero_sprite, enemy_sprite, on_event=log_event)
        # create battle menu
        battle_menu = Menu(MENU_RECT, BATTLE_OPTIONS, font_menu)
        # set menu level
        menu_level = MAIN_MENU
        # set pending events
        pending_events = []

    def choose_action(index):
        """Select action in the battle menu."""
        # use nonlocal to modify menu_level
        nonlocal menu_level
        if menu_level == MAIN_MENU:
            if index == 0:    # Attack
                resolve_turn("attack")
            elif index == 1:  # Skill
                menu_level = SKILL_MENU
                battle_menu.options = SKILL_OPTIONS
                battle_menu.cursor = 0
            elif index == 2:  # Potion
                resolve_turn("potion")
            elif index == 3:  # Flee
                resolve_turn("flee")
        elif menu_level == SKILL_MENU:
            if index == 0:    # Fireball
                resolve_turn("skill", "spell")
            elif index == 1:  # Guard
                resolve_turn("skill", "guard")
            elif index == 2:  # Heal
                resolve_turn("skill", "heal")
            elif index == 3:  # Back
                menu_level = MAIN_MENU
                battle_menu.options = BATTLE_OPTIONS
                battle_menu.cursor = 0

    def resolve_turn(action, skill = None):
        """Resolve the turn"""
        # use nonlocal to modify the state and pending_events variables
        nonlocal state, pending_events
        # get previous number of events
        prev = len(battle.log)
        # player turn
        battle.player_turn(action, skill)
        # get new events
        pending_events = battle.log[prev:]  # only new events (for ANIM)
        # set state ANIM
        state = ANIM

    def update(dt):
        """Update game state."""
        nonlocal state, menu_level, event_player
        # if not ANIM, return
        if state != ANIM:
            return

        # update character animations
        hero_sprite.update(dt)
        enemy_sprite.update(dt)

        # add events to the event player only one time
        if pending_events:
            for event in pending_events:
                event_player.push(event)
            # clear pending events
            pending_events.clear()

        # update event_player
        event_player.update(dt)

        # check if battle is finished only when animation ends
        if event_player.is_idle():
            if battle.is_finished:
                add_result(result=battle.result, turns=battle.turns, hero_hp_left=battle.hero.hp, hero_hp_max=battle.hero.max_hp, enemy_name=battle.enemy.name)
                state = END
            # if not finished, return to battle
            else:
                state = BATTLE
                menu_level = MAIN_MENU
                battle_menu.options = BATTLE_OPTIONS
                battle_menu.cursor = 0

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------
    while running:
        # update the clock
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        # handle events, including quitting the game
        handle_events()

        # update (empty for now; ANIM will use it)
        update(dt)

        # handle drawing
        handle_draw()

    # quit pygame when the main loop ends
    pygame.quit()


# --- Draw Helpers ---
def format_summary_lines(stats):
    """Turn the summary dict into a list of text lines."""
    # create list of lines from the summary dictionary
    lines = [
        f"Total Battles: {stats['total_battles']}",
        f"Victories: {stats['victories']}",
        f"Defeats: {stats['defeats']}",
        f"Flees: {stats['flees']}",
    ]
    # add the most common enemy if it exists
    if stats['most_common_enemy']:
        lines.append(f"Most Common Enemy: {stats['most_common_enemy']}")
    # return the list of lines
    return lines


def draw_lines_centered(screen, font, lines, y):
    """Draw lines centered on screen"""
    for line in lines:
        text = font.render(line, True, COLOR_TEXT)
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, y)
        screen.blit(text, text_rect)
        y += font.get_linesize()


def draw_hint(screen, font):
    """Draw hint"""
    text = font.render("Press any key or click to continue...", True, COLOR_TEXT)
    text_rect = text.get_rect()
    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
    screen.blit(text, text_rect)


def draw_summary_and_hint(screen, menu_font, stats, y):
    """Draw summary and hint"""
    # draw the summary
    draw_lines_centered(screen, menu_font, format_summary_lines(stats), y)
    # draw the hint
    draw_hint(screen, menu_font)


def draw_battle_screen(screen, hero_sprite, enemy_sprite, font_hud, battle_log, font_log, battle_menu, show_menu=True, event_player=None):
    """Draw battle screen"""
    if hero_sprite is None or enemy_sprite is None:
        return

    # draw hero and enemy sprites (the enemy first, so the hero appears on top)
    enemy_sprite.draw(screen)
    hero_sprite.draw(screen)

    # draw hud for hero and enemy
    draw_hud(screen, hero_sprite, font_hud, HERO_CARD_RECT)
    draw_enemy_name(screen, enemy_sprite, font_hud)

    # if event_player is not None, draw it
    if event_player is not None:
        event_player.draw(screen)

    # draw battle log
    battle_log.draw(screen, font_log)

    # draw menu if show_menu is True
    if show_menu:
        battle_menu.draw(screen)


def draw_end_screen(screen, title_font, menu_font, battle, stats):
    """Draw the battle result, a flavor line and the global summary."""
    # get the result of the battle
    result_text = {
        RESULT_VICTORY: "Victory!",
        RESULT_DEFEAT: "Defeat",
        RESULT_FLED: "Fled from battle",
    }[battle.result]

    # render the result
    title = title_font.render(result_text, True, COLOR_TEXT)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 90))
    # render the flavor line
    flavor = f"{battle.hero.name} vs {battle.enemy.name} - {battle.turns} turns"
    text = menu_font.render(flavor, True, COLOR_TEXT)
    screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, 170))
    # draw summary and hint
    draw_summary_and_hint(screen, menu_font, stats, 250)


def draw_stats_screen(screen, title_font, menu_font, stats):
    """Draw the global statistics screen."""
    # render the title
    title = title_font.render("Statistics", True, COLOR_TEXT)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 90))
    # draw summary and hint
    draw_summary_and_hint(screen, menu_font, stats, 250)


if __name__ == "__main__":
    main()
