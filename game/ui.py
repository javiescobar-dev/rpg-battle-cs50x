# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""User interface: handles rendering and user input.
The UI class is responsible for displaying the battle state, including health bars, mana bars, and action menus.
It also captures user input for actions like attack, spell casting, guarding, using potions, and fleeing."""

import pygame
from game.config import COLOR_BORDER, COLOR_TEXT

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
