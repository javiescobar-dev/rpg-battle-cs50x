# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Sprite loader for Pixel Champions II characters.

Supports extracting all animation poses from character sprite sheets
following the game's standard format.
"""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT


def load_character_sprites(path):
    """Load a Pixel Champions II sprite sheet and extract all animation poses.

    Sheet format: 864x576 (96px frames), 6 rows x 9 cols.
    Each row has 3 poses of 3 frames each.
    Returns a dict: { "idle": [frame0, frame1, frame2], "lunge": [...], ... }
    """

    # load image from path
    sheet = pygame.image.load(path).convert_alpha()
    CELL = 96  # pixels per frame

    # each row has 3 poses, each pose has 3 frames
    POSES_PER_ROW = [
        ["idle",      "lunge",     "flee"],
        ["ready_atk", "right_arm", "victory"],
        ["ready_mag", "shoot_mag", "caution"],
        ["defend",    "special",   "abnormal"],
        ["hit",       "use_magic", "sleep"],
        ["evade",     "potion",    "defeated"],
    ]

    # create animations dict
    animations = {}

    # loop and get each animation's frames from the sprite sheet
    for row_idx, pose_names in enumerate(POSES_PER_ROW):
        for pose_idx, pose_name in enumerate(pose_names):
            frames = []
            for frame in range(3):
                col = pose_idx * 3 + frame
                rect = pygame.Rect(col * CELL, row_idx * CELL, CELL, CELL)
                frames.append(sheet.subsurface(rect).copy())
            animations[pose_name] = frames

    # add extra animation "run" based on flee animation, but horizontally flipped
    animations["run"] = [pygame.transform.flip(f, True, False) for f in animations["flee"]]

    # return the animations dict
    return animations


def load_background(path):
    """Load a battle background and scale it to the screen size."""
    bg = pygame.image.load(path).convert()
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# sound effects cache
_sounds = {}

def load_sound(path):
    """Load a sound effect."""
    if path not in _sounds:
        _sounds[path] = pygame.mixer.Sound(path)
    return _sounds[path]



def play_sound(path):
    """Play a sound effect."""
    load_sound(path).play()
