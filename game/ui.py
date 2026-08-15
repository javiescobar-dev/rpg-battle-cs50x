# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Rendering layer for the battle screen.

CharacterSprite draws a character placeholder and its HP/MP bars,
and LogPanel renders the formatted battle log. Step 5 adds the
animation classes here.
"""

import pygame
from collections import deque
from game.config import (
    COLOR_BORDER, COLOR_TEXT, COLOR_BAR_BG, BAR_HEIGHT, COLOR_HP_BAR, COLOR_MP_BAR, COLOR_ACCENT, ENEMY_NAME_RECT,
    LUNGE_DURATION, FLASH_DURATION, RECOIL_DURATION, FLOAT_DURATION, LUNGE_DISTANCE, RECOIL_DISTANCE, FLASH_RADIUS, FLASH_COLOR,
    COLOR_DAMAGE, COLOR_CRIT, FLOAT_SPEED, FONT_FLOAT_SIZE, FONT_CRIT_SIZE, FONT_NAME, COLOR_HEAL, COLOR_GUARD, COLOR_GRAY
)

class Animation:
    """Base class for one-shot timed effects driven by dt (never sleep)."""
    def __init__(self, duration):
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        """Advance the animation by dt (seconds)."""
        self.elapsed += dt

    def is_done(self):
        """Return True when the animation has finished."""
        return self.elapsed >= self.duration

    def draw(self, surface):
        """Draw the effect. Base class draws nothing."""
        pass


class AttackAnimation(Animation):
    """Implements the attacker's movement (lunge forward and recoil) and the hit flash."""
    def __init__(self, attacker, defender, event):
        # set base duration all animations will last this amount of time (seconds)
        super().__init__(LUNGE_DURATION + FLASH_DURATION + RECOIL_DURATION + FLOAT_DURATION)

        self.attacker = attacker
        self.defender = defender
        self.event = event
        self.damage = event.get("damage", 0)
        self.is_crit = event.get("is_crit", False)
        # The direction of the animation (1 if defender is to the right of the attacker, -1 if defender is to the left of the attacker)
        self.sign = 1 if defender.x > attacker.x else -1

        # distances for the animation phases based on scale
        self.lunge   = LUNGE_DISTANCE * attacker.scale
        self.recoil  = RECOIL_DISTANCE * defender.scale

        # create font
        self.font = pygame.font.SysFont(FONT_NAME, FONT_CRIT_SIZE if self.is_crit else FONT_FLOAT_SIZE)

    def _phase(self):
        """Return the current phase name based on elapsed time."""
        if self.elapsed < LUNGE_DURATION:
            return "lunge"
        if self.elapsed < LUNGE_DURATION + FLASH_DURATION:
            return "flash"
        if self.elapsed < LUNGE_DURATION + FLASH_DURATION + RECOIL_DURATION:
            return "recoil"
        return "float"

    def update(self, dt):
        """Update the animation state based on elapsed time."""
        super().update(dt)
        phase = self._phase()

        # calculate the attacker's offset based on the current phase
        if phase == "lunge":
            progress = self.elapsed / LUNGE_DURATION  # 0 -> 1
            self.attacker.offset = self.sign * self.lunge * progress
        elif phase == "flash":
            self.attacker.offset = self.sign * self.lunge  # attacker stays at max extension
        elif phase == "recoil":
            progress = (self.elapsed - LUNGE_DURATION - FLASH_DURATION) / RECOIL_DURATION   # 0 -> 1
            self.defender.offset = -self.sign * self.recoil * progress     # knocked back
        elif phase == "float":
            progress = (self.elapsed - LUNGE_DURATION - FLASH_DURATION - RECOIL_DURATION) / FLOAT_DURATION
            self.attacker.offset = self.sign * self.lunge * (1 - progress)   # go back to original position
            self.defender.offset = -self.sign * self.recoil * (1 - progress)  # go back to original position

        # reset attacker and defender offsets once the full animation completes
        if self.is_done():
            self.attacker.offset = 0  # stay at original position
            self.defender.offset = 0  # stay at original position

    def draw(self, surface):
        """Draw the animation (centered on attacker/defender)."""
        phase = self._phase()
        if phase == "flash":
            self._draw_flash(surface)
        elif phase == "float":
            self._draw_float(surface)

    def _draw_flash(self, surface):
        """Draw a fading flash circle over the defender."""
        progress = (self.elapsed - LUNGE_DURATION) / FLASH_DURATION   # 0 -> 1
        alpha = int(255 * (1 - progress))                             # fade out
        radius = FLASH_RADIUS
        # Create an overlay surface for the flash
        overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Draw the flash circle on the overlay surface
        pygame.draw.circle(overlay, (*FLASH_COLOR, alpha), (radius, radius), radius)
        # Blit the overlay surface on the screen
        surface.blit(overlay, (self.defender.x - radius, self.defender.y - radius))

    def _draw_float(self, surface):
        """Draw the floating damage number rising and fading."""
        # calculate elapsed time for the float phase
        float_elapsed = self.elapsed - LUNGE_DURATION - FLASH_DURATION - RECOIL_DURATION
        # calculate progress (0 -> 1)
        progress = float_elapsed / FLOAT_DURATION                       # 0 -> 1
        # set text based on if the hit was a critical hit
        text = f"{self.damage}!" if self.is_crit else str(self.damage)  # "12!" on crit
        # render the text
        rendered = self.font.render(text, True, COLOR_CRIT if self.is_crit else COLOR_DAMAGE)
        # set the alpha of the text based on the progress
        rendered.set_alpha(int(255 * (1 - progress)))                   # fade out
        # calculate the y position of the text
        y = self.defender.y - 30 * self.defender.scale - FLOAT_SPEED * float_elapsed
        surface.blit(rendered, (self.defender.x - rendered.get_width() // 2, y))


class SpellAnimation(AttackAnimation):
    """Spell attack. Identical to AttackAnimation in Phase 2."""
    pass


class TextAnimation(Animation):
    """Shows a floating message that rises and fades above a sprite."""
    def __init__(self, sprite, text, color):
        # create an object that inherits from Animation with the duration of the animation
        super().__init__(FLOAT_DURATION)
        # set the sprite, text, color and font
        self.sprite = sprite
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(FONT_NAME, FONT_FLOAT_SIZE)

    def draw(self, surface):
        """Draw the text animation."""
        # calculate progress (0 -> 1)
        progress = self.elapsed / FLOAT_DURATION                       # 0 -> 1
        # render the text
        rendered = self.font.render(self.text, True, self.color)
        # set the alpha of the text based on the progress
        rendered.set_alpha(int(255 * (1 - progress)))                   # fade out
        # calculate the y position of the text
        y = self.sprite.y - 30 * self.sprite.scale - FLOAT_SPEED * self.elapsed
        # blit the text on the screen
        surface.blit(rendered, (self.sprite.x - rendered.get_width() // 2, y))


class EventPlayer:
    """Plays battle events as animations, one at a time, driven by dt."""
    def __init__(self, hero_sprite, enemy_sprite, on_event=None):
        # map each Character to its sprite, so events (which carry Characters) resolve to sprites
        self.sprites = {
            hero_sprite.character: hero_sprite,
            enemy_sprite.character: enemy_sprite,
        }
        self.on_event = on_event   # optional callback(event) fired when an animation starts
        self.queue = deque()       # pending events
        self.current = None        # active Animation or None

    def push(self, event):
        """Queue an event to be animated."""
        self.queue.append(event)

    def _make_animation(self, event):
        """Build the right Animation for an event."""
        # get the action from the event
        action = event["action"]

        # if the action is attack, create an AttackAnimation
        if action == "attack":
            return AttackAnimation(self._sprite_of(event["attacker"]), self._sprite_of(event["defender"]), event)
        # if the action is spell, create a SpellAnimation
        elif action == "spell":
            return SpellAnimation(self._sprite_of(event["attacker"]), self._sprite_of(event["defender"]), event)

        # get the actor from the event. "defeated" has no "actor"
        actor = self._sprite_of(event.get("actor") or event.get("defender"))
        # get the text and color for the event
        text, color = self._text_for(event)
        # create a TextAnimation for the event
        return TextAnimation(actor, text, color)

    def _sprite_of(self, character):
        """Return the sprite of a character."""
        return self.sprites[character]

    def _text_for(self, event):
        """Return text and color for a given event."""
        # get the action from the event
        action = event["action"]

        # for every possible action, return the text and color for it
        if action == "guard":
            return "Guard", COLOR_GUARD
        elif action == "heal" or action == "potion":
            return f"+{event['amount']}", COLOR_HEAL
        elif action == "mana_fail":
            return "Not enough mana", COLOR_GRAY
        elif action == "potion_fail":
            return "No potions left", COLOR_GRAY
        elif action == "flee_success":
            return "Fled!", COLOR_GRAY
        elif action == "flee_fail":
            return "Failed to flee!", COLOR_GRAY
        elif action == "defeated":
            return "Defeated!", COLOR_CRIT

        # for every other case, return the event as a string and COLOR_GRAY
        return str(event), COLOR_GRAY

    def update(self, dt):
        """Advance the current animation; pull the next event when it finishes."""
        # if there is no current animation and there is a queue, pop the next event
        if self.current is None and self.queue:
            event = self.queue.popleft()
            self.current = self._make_animation(event)
            # if there is an on_event callback, call it with the event
            if self.on_event:
                self.on_event(event)
        # if there is a current animation, update it
        if self.current is not None:
            self.current.update(dt)
            # if the current animation is done, set it to None
            if self.current.is_done():
                self.current = None

    def is_idle(self):
        """True when no animation is playing or waiting."""
        return self.current is None and not self.queue

    def draw(self, surface):
        """Draw the active animation effect on top of the sprites."""
        if self.current is not None:
            self.current.draw(surface)


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
