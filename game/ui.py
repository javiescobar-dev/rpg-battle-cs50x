# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Rendering layer for the battle screen.

CharacterSprite draws a character placeholder and its HP/MP bars,
and LogPanel renders the formatted battle log. Step 5 adds the
animation classes here.
"""

import pygame
from collections import deque
from game.config import COLOR_BORDER, COLOR_TEXT, COLOR_BAR_BG, BAR_HEIGHT, COLOR_HP_BAR, COLOR_MP_BAR, COLOR_ACCENT, ENEMY_NAME_RECT

# Base class for sprite of characters
class CharacterSprite:
    """Wraps a Character and draws it as a placeholder built with primitives."""
    def __init__(self, character, x, y, color, scale=1.0):
        self.character = character
        self.x = x
        self.y = y
        self.color = color  # Color to represent the character (for placeholder purposes)
        self.scale = scale
        self.offset = 0     # Offset for simple animation

    def draw(self, surface):
        """Draw the character as a placeholder rectangle with a border and a head."""
        # Calculate the position with offset for simple animation
        x = self.x + self.offset
        width = int(60 * self.scale)
        height = int(80 * self.scale)
        # Draw the character's body as a rectangle with a border and a head
        body = pygame.Rect(x - width // 2, self.y - height // 2, width, height)
        pygame.draw.rect(surface, self.color, body)  # Draw the character's body
        pygame.draw.rect(surface, COLOR_BORDER, body, 2)  # Draw the border of the character's body
        # Draw eyes
        eye_dx = int(10 * self.scale)
        eye_y  = self.y - int(22 * self.scale)
        radius = max(2, int(4 * self.scale))  # ensure radius is at least 2 px with max scale
        pygame.draw.circle(surface, COLOR_TEXT, (x - eye_dx, eye_y), radius)
        pygame.draw.circle(surface, COLOR_TEXT, (x + eye_dx, eye_y), radius)


# class to display battle log
class LogPanel:
    """Displays the last N battle log messages inside a panel."""

    def __init__(self, rect, max_messages=6):
        self.rect = pygame.Rect(rect)
        # deque = queue with maximum length, removes the old value when a new one exceeds the maximum length limit
        self.messages = deque(maxlen=max_messages)

    # method to add message to the queue
    def add(self, text):
        self.messages.append(text)

    # method to wrap text into lines that fit within max_width pixels
    def _wrap(self, font, text, max_width):
        """Split text into lines that fit within max_width pixels."""
        lines = []
        current = ""
        # iterate over the words in the text
        for word in text.split(" "):
            candidate = current + " " + word if current else word
            # if the candidate text fits within max_width pixels, update the current text
            if font.size(candidate)[0] <= max_width:
                current = candidate
            # if the candidate text does not fit within max_width pixels, add the current text to the lines and update the current text
            else:
                lines.append(current)
                current = word
        # if the current text is not empty, add it to the lines
        if current:
            lines.append(current)
        return lines

    # method to draw the box of the log and show messages of the battle
    def draw(self, surface, font):
        # draw the box of the log
        pygame.draw.rect(surface, COLOR_BAR_BG, self.rect)
        # draw the border of the log
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, 2)
        # calculate max width for the lines
        max_width = self.rect.width - 10
        # create a list of wrapped lines from the messages in the queue (top to bottom)
        lines = [wrapped for text in self.messages
                for wrapped in self._wrap(font, text, max_width)]
        # calculate height position of first line
        y = self.rect.bottom - 8
        # iterate over the lines of messages (in reverse order) so the last message is at the bottom
        for line in reversed(lines):
            # get height of the line
            height = font.get_height()
            # stop rendering if we run out of panel height
            if y - height < self.rect.top + 8:
                break
            # render each line
            rendered = font.render(line, True, COLOR_TEXT)
            # blit the line on the surface
            surface.blit(rendered, (self.rect.left + 8, y - height))
            # update height position of next line
            y -= height + 4


# class menu (with methods to draw options and manage keyboard/mouse input)
class Menu:
    """Show menu options, manage selection and highlight"""
    def __init__(self, rect, options, font):
        self.rect = pygame.Rect(rect)  # panel for menu
        self.options = options  # list of options (attack, skill, etc)
        self.font = font  # font to render options
        self.cursor = 0  # index of the currently selected option

    def move_cursor(self, delta):
        """Move cursor up or down, wrapping around the ends.

        Args:
            delta: +1 to move down, -1 to move up
        """
        # store the current selection, module (%) is used to wrap around the ends
        # (if cursor > options, it goes to the end; if cursor < 0, it goes to the begining)
        self.cursor = (self.cursor + delta) % len(self.options)

    def index_at(self, pos):
        """Convert a pixel position into an option index (0-based), or return None if outside the menu area.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            The index of the option at the given position, or None if outside the menu area.
        """
        # convert screen coordinates to coordinates relative to the menu's top-left corner
        x, y = pos

        # height of each row (option)
        row_height = self.font.get_height() + 8

        # check if pos is inside the menu area
        if not self.rect.collidepoint(x, y):
            return None

        # calculate the row index, rect.top convert to local coords of the panel
        index = (y - self.rect.top) // row_height

        # check if index is within the range of the options
        if 0 <= index < len(self.options):
            return index

        return None

    def handle_click(self, pos):
        """Handle a mouse click on the menu.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            The index of the option clicked, or None if no option was clicked.
        """

        # by now only return the index of the option, later can be used to implement click logic
        return self.index_at(pos)

    def draw(self, surface):
        """Draw menu options on a panel at the bottom right of the screen.

        Args:
            surface: pygame surface to draw on
        """

        # Draw the background of the menu panel
        pygame.draw.rect(surface, COLOR_BAR_BG, self.rect)
        # Draw the border of the menu panel
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, 2)

        # get the height of each row (option)
        row_height = self.font.get_height() + 8

        # iterate over every option
        for i, option in enumerate(self.options):
            # calculate the rectangle for each option
            row_rect = pygame.Rect(self.rect.left, self.rect.top + i * row_height, self.rect.width, row_height)

            # highlight row if cursor is on it (is the current option selected by keyboard or mouse)
            if i == self.cursor:
                pygame.draw.rect(surface, COLOR_ACCENT, row_rect)
            # render option text
            text = self.font.render(option, True, COLOR_TEXT)
            # blit (draw) the option text centered in its row (half of the row height and half of the text height)
            surface.blit(text, (row_rect.centerx - text.get_width() // 2, row_rect.centery - text.get_height() // 2))


# methods to draw HUD
def draw_bar(surface, x, y, width, height, current_value, max_value, color):
    """Draw a proportional fill bar with background and border."""
    # Draw the background of the bar
    pygame.draw.rect(surface, COLOR_BAR_BG, (x, y, width, height))
    # Calculate the fill width based on current value and max value
    fill = int(width * current_value / max_value)
    # Draw the filled portion of the bar
    pygame.draw.rect(surface, color, (x, y, fill, height))
    # Draw the border of the bar
    pygame.draw.rect(surface, COLOR_BORDER, (x, y, width, height), 2)


def draw_hud(surface, sprite, font, rect):
    """Draw a fixed status card (Name, Health and Mana bars) at the given rect."""
    # get character of sprite
    char = sprite.character
    card = pygame.Rect(rect)                       # position comes from the caller
    # frame: background + border, same style as the other panels
    pygame.draw.rect(surface, COLOR_BAR_BG, card)
    pygame.draw.rect(surface, COLOR_BORDER, card, 2)
    # name centered at the top of the card
    name = font.render(char.name, True, COLOR_TEXT)
    surface.blit(name, (card.centerx - name.get_width() // 2, card.top + 4))
    # HP and MP bars inside the card
    bar_width = card.width - 12
    draw_bar(surface, card.left + 6, card.top + 24, bar_width, BAR_HEIGHT, char.hp, char.max_hp, COLOR_HP_BAR)
    draw_bar(surface, card.left + 6, card.top + 38, bar_width, BAR_HEIGHT, char.mp, char.max_mp, COLOR_MP_BAR)


def draw_enemy_name(surface, sprite, font):
    """Draw the enemy's name above the enemy sprite."""
    # get character of sprite
    char = sprite.character
    # get name with render style
    name = font.render(char.name, True, COLOR_TEXT)
    # get rect for the enemy name
    rect = pygame.Rect(ENEMY_NAME_RECT)
    # plate background + frame
    pygame.draw.rect(surface, COLOR_BAR_BG, rect)
    pygame.draw.rect(surface, COLOR_BORDER, rect, 2)
    # Draw the enemy's name centered in its rectangle, blit needs a tuple (x, y), not two separate numbers
    surface.blit(name, (rect.centerx - name.get_width() // 2, rect.centery - name.get_height() // 2))
