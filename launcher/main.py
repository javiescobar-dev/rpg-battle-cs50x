# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Main launcher window and UI logic."""

import threading, io, urllib.request
import customtkinter as ctk
from PIL import Image

from ui_styles import *
from config import APP_NAME, APP_VERSION
from paths import installed_version, is_game_installed, launch_game
from updater import fetch_latest_release, find_asset, update
from news import get_news


class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # window settings
        ctk.set_appearance_mode(APPEARANCE_MODE)          # set appearance mode (Light/Dark)
        self.title(APP_NAME)                              # set window title
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # set window size
        self.resizable(False, False)                      # set window to not be resizable
        self.configure(fg_color=BG_COLOR)                 # set window background color

        # internal state
        self._current_tab = "news"                        # default tab
        self._latest_release = None                       # stores the latest release from server

        # build UI
        self._build_sidebar()                             # build the sidebar
        self._build_content()                             # build the content area
        self._build_footer()                              # build the footer

        # initial load in background
        self.after(100, self._startup)                  # start loading data in background (call _startup after 100ms)

    def _startup(self):
        """Load initial data in background."""
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        """Load release info and news from server."""
        try:
            self._latest_release = fetch_latest_release()
        except Exception:
            self._latest_release = None

        # temp: prints in console for verification
        print("Release:", self._latest_release.get("tag_name") if self._latest_release else "None")
        print("Installed:", installed_version())