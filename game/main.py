# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""
Run a playable turn-based battle with simple graphics.
"""

import pygame
from game.battle import Battle, format_event
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG,
    HERO_X, ENEMY_X, ARENA_Y, LOG_RECT,
    COLOR_HERO, COLOR_ENEMY, FONT_NAME, FONT_HUD_SIZE, FONT_LOG_SIZE,
)
from game.entities import make_hero, make_enemy
from game.ui import CharacterSprite, LogPanel, draw_hud


def main():
    """Run the pygame window main loop."""

    # initialize pygame (events, video, audio, etc.)
    pygame.init()

    # set up the display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # set the window title
    pygame.display.set_caption("RPG Battle")

    # create a clock to manage the frame rate (limit game to 60 FPS and return the time since the last frame in seconds)
    clock = pygame.time.Clock()

    # set the running flag to True to enter the main loop
    running = True

    # --- TEMPORARY preview (replaced by the state machine in step 4) ---
    # create a battle with a hero and an enemy
    battle = Battle(make_hero(), make_enemy())

    # player turns
    battle.player_turn("attack")
    battle.player_turn("skill", "spell")
    battle.player_turn("potion")

    # create fonts for HUD and log
    font_hud = pygame.font.SysFont(FONT_NAME, FONT_HUD_SIZE)
    font_log = pygame.font.SysFont(FONT_NAME, FONT_LOG_SIZE)

    # create sprites for hero and enemy
    hero_sprite = CharacterSprite(battle.hero, HERO_X, ARENA_Y, COLOR_HERO)
    enemy_sprite = CharacterSprite(battle.enemy, ENEMY_X, ARENA_Y, COLOR_ENEMY)

    # create log panel
    log = LogPanel(LOG_RECT)
    for event in battle.log:
        log.add(format_event(event))

    while running:
        # update the clock
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        # handle events, including quitting the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with the background color
        screen.fill(COLOR_BG)

        # draw sprites, hud and log
        hero_sprite.draw(screen)
        enemy_sprite.draw(screen)
        draw_hud(screen, hero_sprite, font_hud)
        draw_hud(screen, enemy_sprite, font_hud)
        log.draw(screen, font_log)

        # update the display
        pygame.display.flip()

    # quit pygame when the main loop ends
    pygame.quit()

if __name__ == "__main__":
    main()
