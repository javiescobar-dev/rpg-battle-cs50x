# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""CustomTkinter style constants and theme configuration."""

# Active theme ('Light' or 'Dark'). Set at startup by main.py / settings.
CURRENT_THEME = "Light"

# Light theme: blue game colors on a pale background
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

# Dark theme: dark blue background, neon-like cyan accents
DARK = {
    "bg": "#14141E",
    "panel": "#1E1E2E",
    "border": "#2A3A55",
    "accent": "#E6D150",
    "hover": "#E6C038",
    "button_text": "#10141C",
    "text_title": "#E6E6E6",
    "text_body": "#C0C8D0",
    "text_date": "#F0A050",
    "scrollbar": "#2A3A55",
}

THEMES = {"Light": LIGHT, "Dark": DARK}


def THEME() -> dict:
    """Return the color dictionary of the active theme."""
    return THEMES[CURRENT_THEME]


# Fonts (theme-independent)
FONT_TITLE = ("Georgia", 18, "bold")
FONT_BODY  = ("Arial", 13)
FONT_DATE  = ("Arial", 11)

# Dimensions
WINDOW_WIDTH  = 960
WINDOW_HEIGHT = 600

HEADER_HEIGHT = 50
FOOTER_HEIGHT = 100
FOOTER_TOP_HEIGHT = 58
