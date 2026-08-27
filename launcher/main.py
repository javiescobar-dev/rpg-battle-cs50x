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

    def _build_sidebar(self):
        """Left sidebar with navigation buttons."""
        # Sidebar frame
        self._sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, fg_color=SIDEBAR_BG, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)  # prevents sidebar from resizing

        # Sidebar title (vertical)
        ctk.CTkLabel(self._sidebar, text="RPG\nB", font=("Georgia", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=(20, 30))

        # news button
        self._btn_news = ctk.CTkButton(
            self._sidebar, text="NEWS",
            font=FONT_SIDEBAR, fg_color="transparent",
            text_color=TEXT_TITLE, hover_color=BORDER_COLOR,
            command=lambda: self._show_tab("news")
        )
        self._btn_news.pack(fill="x", padx=8, pady=4)

        # settings button
        self._btn_settings = ctk.CTkButton(
            self._sidebar, text="SETTINGS",
            font=FONT_SIDEBAR, fg_color="transparent",
            text_color=TEXT_TITLE, hover_color=BORDER_COLOR,
            command=lambda: self._show_tab("settings")
        )
        self._btn_settings.pack(fill="x", padx=8, pady=4)

    def _show_tab(self, tab_name):
        """Show the indicated tab and hide the others."""
        self._current_tab = tab_name  # set the current tab

        # show or hide the news tab
        if tab_name == "news":
            self._news_frame.pack(side="top", fill="both", expand=True, padx=16, pady=(0, 10))  # show news tab
            self._settings_frame.pack_forget()  # hide settings tab
        else:
            self._settings_frame.pack(side="top", fill="both", expand=True, padx=16, pady=(0, 10))  # show settings tab
            self._news_frame.pack_forget()  # hide news tab

    def _build_content(self):
        """Central scrollable panel containing the tabs."""
        # Central panel
        self._content = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

        # News frame (scrollable)
        self._news_frame = ctk.CTkScrollableFrame(
            self._content, fg_color=BG_COLOR,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=ACCENT_COLOR
        )

        # Placeholder: message while loading
        self._news_placeholder = ctk.CTkLabel(
            self._news_frame, text="Loading news...",
            font=FONT_BODY, text_color=TEXT_DATE
        )
        self._news_placeholder.pack(pady=40)

        # Settings frame (placeholder)
        self._settings_frame = ctk.CTkFrame(
            self._content, fg_color=BG_COLOR
        )
        self._settings_frame.pack_forget()  # hidden at the start

        # Settings header
        ctk.CTkLabel(self._settings_frame, text="Settings", font=FONT_TITLE, text_color=TEXT_TITLE).pack(pady=(40, 10))

        # Settings body
        ctk.CTkLabel(
            self._settings_frame,
            text=f"{APP_NAME} v{APP_VERSION}\n\nGame data is stored in your\nplatform's user data directory.",
            font=FONT_BODY, text_color=TEXT_BODY, justify="center"
        ).pack(pady=10)

        # Show news by default
        self._show_tab("news")

    def _build_footer(self):
        """Bottom bar: versions, buttons and progress bar."""
        # Footer frame
        footer = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0, height=60)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        # Top row: labels + buttons
        row = ctk.CTkFrame(footer, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(8, 2))

        # Installed version
        installed = installed_version()
        self._lbl_installed = ctk.CTkLabel(row, text=f"Installed: {installed}" if installed else "Installed: —", font=FONT_DATE, text_color=TEXT_BODY)
        self._lbl_installed.pack(side="left")

        # Remote version (filled later)
        self._lbl_latest = ctk.CTkLabel(row, text="Latest: ...", font=FONT_DATE, text_color=TEXT_BODY)
        self._lbl_latest.pack(side="left", padx=(20, 0))

        # Check button
        self._btn_check = ctk.CTkButton(
            row, text="Check", width=70, height=28,
            font=FONT_DATE, fg_color=ACCENT_COLOR,
            hover_color=BUTTON_HOVER, text_color=BUTTON_TEXT,
            command=self._on_check_click
        )
        self._btn_check.pack(side="right", padx=(8, 0))

        # Play button
        self._btn_play = ctk.CTkButton(
            row, text="Play", width=90, height=28,
            font=FONT_DATE, fg_color=ACCENT_COLOR,
            hover_color=BUTTON_HOVER, text_color=BUTTON_TEXT,
            command=self._on_play_click
        )
        self._btn_play.pack(side="right", padx=(8, 0))

        # Download / Update button
        self._btn_download = ctk.CTkButton(
            row, text="Download", width=90, height=28,
            font=FONT_DATE, fg_color=ACCENT_COLOR,
            hover_color=BUTTON_HOVER, text_color=BUTTON_TEXT,
            command=self._on_download_click
        )
        self._btn_download.pack(side="right")

        # Initial state of the Play button (disabled if the game is not installed)
        if not is_game_installed():
            self._btn_play.configure(state="disabled")

        # Bottom row: progress bar (hidden at the start)
        self._progress = ctk.CTkProgressBar(footer, fg_color=BORDER_COLOR, progress_color=ACCENT_COLOR, height=6)
        self._progress.set(0)
        # Not packed here - shown only during download

    def _on_check_click(self):
        """Check the latest remote version."""
        pass

    def _on_play_click(self):
        """Launch the game."""
        pass

    def _on_download_click(self):
        """Download or update the game."""
        pass
