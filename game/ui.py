# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""pygame entry point for the game.

Opens the game window and runs the main loop with the classic
events -> update -> draw cycle. This version shows a static battle
preview; step 4 replaces it with the MENU/BATTLE/ANIM/END/STATS
state machine.
"""

import pygame
from collections import deque
from game.config import COLOR_BORDER, COLOR_TEXT, COLOR_BAR_BG, BAR_WIDTH, BAR_HEIGHT, COLOR_HP_BAR, COLOR_MP_BAR

# Base class for sprite of characters
class CharacterSprite:
    """Wraps a Character and draws it as a placeholder built with primitives."""
    def __init__(self, character, x, y, color):
        self.character = character
        self.x = x
        self.y = y
        self.color = color  # Color to represent the character (for placeholder purposes)
        self.offset = 0     # Offset for simple animation


    def draw(self, surface):
        """Draw the character as a placeholder rectangle with a border and a head."""
        # Calculate the position with offset for simple animation
        x = self.x + self.offset
        # Draw the character's body as a rectangle with a border and a head
        body = pygame.Rect(x - 30, self.y - 40, 60, 80)  # Placeholder rectangle for the character
        pygame.draw.rect(surface, self.color, body)  # Draw the character's body
        pygame.draw.rect(surface, COLOR_BORDER, body, 2)  # Draw the border of the character's body
        pygame.draw.circle(surface, COLOR_TEXT, (x - 10, self.y - 22), 4)  # Draw the character's eye (left)
        pygame.draw.circle(surface, COLOR_TEXT, (x + 10, self.y - 22), 4)  # Draw the character's eye (right)


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


def draw_hud(surface, sprite, font):
    """Draw the HUD (Name, Health and Mana bars) above a character sprite."""
    # get character of sprite
    char = sprite.character
    # get x position of sprite
    x = sprite.x - BAR_WIDTH // 2
    # get name with render style
    name = font.render(char.name, True, COLOR_TEXT)
    # Draw the character's name above the sprite
    surface.blit(name, (sprite.x - name.get_width() // 2, sprite.y - 100))
    draw_bar(surface, x, sprite.y - 78, BAR_WIDTH, BAR_HEIGHT, char.hp, char.max_hp, COLOR_HP_BAR)
    draw_bar(surface, x, sprite.y - 62, BAR_WIDTH, BAR_HEIGHT, char.mp, char.max_mp, COLOR_MP_BAR)
