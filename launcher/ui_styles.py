# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""CustomTkinter style constants and theme configuration."""

# Active theme ('Light' or 'Dark'). Set at startup by main.py / settings.
CURRENT_THEME = "Light"

# Light theme: blue game colors on a pale background
LIGHT = {
    "bg": "#FFFFFF",
    "panel": "#FFFFFF",
    "border": "#C3D4E3",
    "border_frame": "#10141C",
    "accent": "#50C8F0",
    "hover": "#38A8D6",
    "hover_header": "#EDF5FF",
    "play_button": "#91D04B",
    "play_button_hover": "#85BE46",
    "play_button_border": "#478F04",
    "uninstall_button": "#DE2F2F",
    "uninstall_button_hover": "#B30000",
    "uninstall_button_border": "#990000",
    "button_text": "#FFFFFF",
    "button_border": "#0B77BA",
    "text_title": "#14222E",
    "text_body": "#3A4A5A",
    "text_date": "#7C8EA0",
    "scrollbar": "#C3D4E3",
    "disabled_fg_color": "#E1E7EE",
    "disabled_border_color": "#CAD4DE",
    "disabled_text_color": "#98A6B5"
}

# Dark theme: dark blue background, neon-like cyan accents
DARK = {
    "bg": "#222222",
    "panel": "#222222",
    "border": "#2A3A55",
    "border_frame": "#000000",
    "accent": "#E6D150",
    "hover": "#E6C038",
    "hover_header": "#2A3A55",
    "play_button": "#91D04B",
    "play_button_hover": "#85BE46",
    "play_button_border": "#000000",
    "uninstall_button": "#C22B2B",
    "uninstall_button_hover": "#B11111",
    "uninstall_button_border": "#990000",
    "button_text": "#10141C",
    "button_border": "#000000",
    "text_title": "#E6E6E6",
    "text_body": "#C0C8D0",
    "text_date": "#F0A050",
    "scrollbar": "#2A3A55",
    "disabled_fg_color": "#333A45",
    "disabled_border_color": "#3D4755",
    "disabled_text_color": "#5A6472"
}

THEMES = {"Light": LIGHT, "Dark": DARK}


def THEME() -> dict:
    """Return the color dictionary of the active theme."""
    return THEMES[CURRENT_THEME]


ICONS = {
    "theme_light": "theme_light_icon",
    "theme_dark": "theme_dark_icon",
    "minimize": "minimize_icon",
    "close": "close_window_icon"
}

# Fonts (theme-independent)
FONT_TITLE  = ("Georgia", 18, "bold")
FONT_BODY   = ("Arial", 13)
FONT_DATE   = ("Arial", 11)
FONT_BOLD   = ("Arial", 12, "bold")
FONT_BUTTON = ("Arial", 14)

# Dimensions
WINDOW_WIDTH  = 960
WINDOW_HEIGHT = 600

HEADER_HEIGHT     = 65
FOOTER_HEIGHT     = 100
FOOTER_TOP_HEIGHT = 58

TITLE_FONT_SIZE   = 38
TITLE_BAR_H       = 1    # bar thickness
TITLE_BAR_GAP     = 2    # gap between text and bar
TITLE_BAR_EXTRA_W = 15   # extra bar width (7.5 on each side)

BUTTON_HEIGHT = 36
