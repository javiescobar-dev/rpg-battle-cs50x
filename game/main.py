# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Console entry point for Phase 1.

Runs a playable turn-based battle in the terminal: main menu, battle UI with
a hybrid log (only new messages plus an always-visible status line), score
recording and statistics. Will be rewritten in phase 2 to launch a pygame
window.
"""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG

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

    while running:
        # update the clock
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        # handle events, including quitting the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with the background color
        screen.fill(COLOR_BG)

        # update the display
        pygame.display.flip()

    # quit pygame when the main loop ends
    pygame.quit()

if __name__ == "__main__":
    main()
