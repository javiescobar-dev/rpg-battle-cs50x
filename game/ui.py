# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""User interface: handles rendering and user input.
The UI class is responsible for displaying the battle state, including health bars, mana bars, and action menus.
It also captures user input for actions like attack, spell casting, guarding, using potions, and fleeing."""

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

    # method to draw the box of the log and show messages of the battle
    def draw(self, surface, font):
        pygame.draw.rect(surface, COLOR_BAR_BG, self.rect)  # TODO: see if need update color
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, 2)
        # Calculate height position of first line
        y = self.rect.top + 8
        # Iterate over the messages in the queue and print it
        for text in self.messages:
            line = font.render(text, True, COLOR_TEXT)
            surface.blit(line, (self.rect.left + 8, y))
            y += line.get_height() + 4


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
    surface.blit(name, (sprite.x - name.get_width() // 2, sprite.y - 48))
    draw_bar(surface, x, sprite.y - 62, BAR_WIDTH, BAR_HEIGHT, char.hp, char.max_hp, COLOR_HP_BAR)
    draw_bar(surface, x, sprite.y - 78, BAR_WIDTH, BAR_HEIGHT, char.mp, char.max_mp, COLOR_MP_BAR)
