# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""CustomTkinter style constants and theme configuration."""

# Appearance (kept for ctk; we manage theme colors manually)
APPEARANCE_MODE = "Light"

# Theme palettes
LIGHT = {
    "bg": "#F4F8FB",
    "panel": "#E4EEF6",
    "border": "#C3D4E3",
    "accent": "#50C8F0",
    "hover": "#38A8D6",
    "button_text": "#FFFFFF",
    "text_title": "#14222E",
    "text_body": "#3A4A5A",
    "text_date": "#7C8EA0",
    "scrollbar": "#C3D4E3",
}
DARK = {
    "bg": "#14141E",
    "panel": "#1E1E2E",
    "border": "#2A3A55",
    "accent": "#50C8F0",
    "hover": "#7CD6FF",
    "button_text": "#10141C",
    "text_title": "#E6E6E6",
    "text_body": "#C0C8D0",
    "text_date": "#7FB8D9",
    "scrollbar": "#2A3A55",
}

THEMES = {"Light": LIGHT, "Dark": DARK}
CURRENT_THEME = "Light"

def THEME():
    """Return the active theme color dictionary."""
    return THEMES[CURRENT_THEME]

# Fonts
FONT_TITLE = ("Georgia", 18, "bold")
FONT_BODY  = ("Arial", 13)
FONT_DATE  = ("Arial", 11)

# Dimensions
WINDOW_WIDTH  = 960
WINDOW_HEIGHT = 600
