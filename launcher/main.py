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
        self.after(100, self._startup)                    # start loading data in background (call _startup after 100ms)

    def _startup(self):
        """Load initial data in background."""
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        """Get release info and news from server (runs in background)."""
        # Release
        try:
            release = fetch_latest_release()
            self._latest_release = release
            tag = release.get("tag_name", "?")
            self.after(0, lambda: self._lbl_latest.configure(text=f"Latest: {tag}"))  # Set the latest release tag in background
        except Exception:
            self.after(0, lambda: self._lbl_latest.configure(text="Latest: —"))  # Set the latest release tag to — if fetch fails

        # News
        items = get_news()
        self.after(0, lambda: self._populate_news(items))

    def _populate_news(self, items):
        """Populates the news frame with the received items."""
        # Remove placeholder
        self._news_placeholder.destroy()

        # If no news available, show a message
        if not items:
            ctk.CTkLabel(self._news_frame, text="No news available.", font=FONT_BODY, text_color=TEXT_DATE).pack(pady=40)
            return

        # Add each news item card to the news frame
        for item in items:
            self._add_news_card(item)

    def _add_news_card(self, item):
        """Adds a news card to the news frame."""
        # Card frame
        card = ctk.CTkFrame(
            self._news_frame, fg_color=SIDEBAR_BG,
            border_width=1, border_color=BORDER_COLOR,
            corner_radius=8
        )
        card.pack(fill="x", pady=(0, CARD_PADDING))

        # Image (loads in background)
        image_url = item.get("image")
        img_label = ctk.CTkLabel(card, text="", height=140)
        img_label.pack(fill="x", padx=CARD_PADDING, pady=(CARD_PADDING, 0))

        # Load image in background (using threading to avoid freezing the UI)
        if image_url:
            threading.Thread(target=self._load_image, args=(image_url, img_label), daemon=True).start()

        # Title + Date
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=CARD_PADDING, pady=(6, 0))

        # Title
        ctk.CTkLabel(
            header, text=item.get("title", "Untitled"),
            font=FONT_TITLE, text_color=TEXT_TITLE, anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Date
        ctk.CTkLabel(
            header, text=item.get("date", ""),
            font=FONT_DATE, text_color=TEXT_DATE
        ).pack(side="right")

        # Body
        ctk.CTkLabel(
            card, text=item.get("body", ""),
            font=FONT_BODY, text_color=TEXT_BODY,
            wraplength=550, justify="left", anchor="w"
        ).pack(fill="x", padx=CARD_PADDING, pady=(4, CARD_PADDING))

    def _load_image(self, url, label):
        """Downloads an image and displays it in the label (in background)."""
        try:
            # Request the image from the URL
            req = urllib.request.Request(url)
            # Open the URL and read the data
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            # Open the image from the data
            img = Image.open(io.BytesIO(data))

            # Resize image to fit the content panel width (~580px)
            width, height = img.size
            new_width = 580  # Content panel width
            new_height = int(height * (new_width / width))  # Maintain aspect ratio
            img = img.resize((new_width, new_height), Image.LANCZOS)  # LANCZOS used for high-quality resizing

            # Create CTkImage and configure the label in the UI thread
            ctk_img = ctk.CTkImage(light_image=img, size=(new_width, new_height))
            self.after(0, lambda: label.configure(image=ctk_img, text=""))
        except Exception:
            # Show error message if image fails to load
            self.after(0, lambda: label.configure(text="[Image not available]", text_color=TEXT_DATE ))

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
        """Check the latest remote version (runs in a background thread)."""
        # default state and text of the check button
        self._btn_check.configure(state="disabled", text="Checking...")

        # thread to check the latest remote version
        def _check():
            try:
                # fetch the latest release
                release = fetch_latest_release()
                self._latest_release = release
                tag = release.get("tag_name", "?")
                # update the latest remote version label
                self.after(0, lambda: self._lbl_latest.configure(text=f"Latest: {tag}"))
            except Exception:
                # update the latest remote version label
                self.after(0, lambda: self._lbl_latest.configure(text="Latest: —"))
            finally:
                # restore the check button
                self.after(0, lambda: self._btn_check.configure(state="normal", text="Check"))

        # start the thread
        threading.Thread(target=_check, daemon=True).start()

    def _on_play_click(self):
        """Launch the game."""
        try:
            # don't need threading because subprocess.Popen inside launch_game has their own process
            launch_game()
        except Exception as e:
            self._lbl_installed.configure(text=f"Error: {e}")

    def _on_download_click(self):
        """Download or update the game (runs in a background thread)."""
        # if latest release is not fetched, return
        if self._latest_release is None:
            return

        # get tag
        tag = self._latest_release.get("tag_name")
        if not tag:
            return

        # disable buttons and show progress bar
        self._btn_download.configure(state="disabled", text="Downloading...")
        self._btn_play.configure(state="disabled")
        self._btn_check.configure(state="disabled")
        self._progress.set(0)
        self._progress.pack(fill="x", padx=16, pady=(0, 8))

        # thread to download the game
        def _do_update():
            # progress callback
            def on_progress(fraction):
                self.after(0, lambda: self._progress.set(fraction))

            # download the game
            success = update(tag, progress_callback=on_progress)

            # finish download (after GUI is ready)
            def _finish():
                # hide progress bar
                self._progress.pack_forget()
                # restore buttons
                self._btn_download.configure(state="normal", text="Download")
                self._btn_check.configure(state="normal")
                # update installed version if successful
                if success:
                    self._lbl_installed.configure(text=f"Installed: {tag}")
                    self._btn_play.configure(state="normal")
                else:
                    self._btn_download.configure(text="Retry")

            # call finish (after GUI is ready)
            self.after(0, _finish)

        # start the thread
        threading.Thread(target=_do_update, daemon=True).start()


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
