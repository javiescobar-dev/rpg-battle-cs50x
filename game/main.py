# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Pygame entry point: MENU / STATS / BATTLE / ANIM / END state machine."""


import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT, FONT_NAME, FONT_TITLE_SIZE, FONT_MENU_SIZE
)
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

    # main game loop
    while running:
        # update the clock
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        # handle events, including quitting the game
        handle_events()

        # update (empty for now; ANIM will use it)
        # TODO

        # handle drawing
        handle_draw()

    # quit pygame when the main loop ends
    pygame.quit()

if __name__ == "__main__":
    main()
