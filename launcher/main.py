# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Main launcher window and UI logic."""

import threading, urllib.request
import customtkinter as ctk
from PIL import Image

import ui_styles as styles
from config import APP_NAME
from paths import installed_version, is_game_installed, launch_game, launcher_background_path
from updater import fetch_latest_release, find_asset, update
from news import get_news
from settings import load_theme, save_theme

class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Restore the last saved theme
        styles.CURRENT_THEME = load_theme()
        ctk.set_appearance_mode(styles.CURRENT_THEME)     # set appearance mode (Light/Dark)

        # Align tk scaling with the fixed window size to avoid the startup resize flash
        self.tk.call('tk', 'scaling', 1.0)

        # Hide the window initially
        self.withdraw()

        # window settings
        ctk.set_window_scaling(1.0)                       # set window scaling
        ctk.set_widget_scaling(1.0)                       # set widget scaling
        self.title(APP_NAME)                              # set window title
        self.geometry(f"{styles.WINDOW_WIDTH}x{styles.WINDOW_HEIGHT}")  # set window size
        self.resizable(False, False)                      # set window to not be resizable
        self.configure(fg_color=styles.THEME()["bg"])     # set window background color

        # internal state
        self._latest_release = None                       # stores the latest release from server
        self._news_items = []                             # stores the news items once loaded
        self._carousel_index = 0                          # which news slide is active
        self._carousel_bg = None                          # stores the carousel background image

        # Build UI
        self._build_header()                              # build the top header
        self._build_content()                             # build the content area
        self._build_footer()                              # build the footer

        # initial load in background
        self.after(100, self._startup)                    # start loading data in background (call _startup after 100ms)

        # show the window once the mainloop is running and the layout is stable
        self.after(1200, self._show_window)

    def _show_window(self):
        """Show the window once the mainloop has stabilized the layout."""
        # Apply the final geometry and show the window without flickering
        self.geometry(f"{styles.WINDOW_WIDTH}x{styles.WINDOW_HEIGHT}")  # re-apply the exact window size
        self.update_idletasks()                   # process any pending geometry updates
        self.deiconify()                          # show the window
        self.lift()                               # bring the window to the front
        self.update_idletasks()                   # process any pending geometry updates (now the layout is truly settled)
        # resize after the window is fully shown; a short delay ensures the CTkImage.configure takes effect on the freshly created label
        self.after(50, self._resize_carousel_bg)  # resize carousel background to fill its frame (after deiconify and final size)

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
        self._news_items = items  # store news items for later use (carousel)
        self.after(0, lambda: self._populate_news(items))

    def _populate_news(self, items):
        """Store news items; the active slide is drawn later via _show_slide."""
        self._news_items = items

        # if no news available, show a message (in the carousel area)
        if not items:
            ctk.CTkLabel(self._content_frame, text="No news available.", font=styles.FONT_BODY, text_color=styles.THEME()["text_date"]).pack(pady=40)
            return

        # TODO: _show_slide(self._carousel_index) will render the active news here (mini-paso 3c)

    def _build_header(self):
        """Top bar with title and placeholder buttons."""
        # Top bar frame (full width, fixed height)
        self._header = ctk.CTkFrame(self, fg_color=styles.THEME()["panel"], corner_radius=0, height=50)
        self._header.pack(side="top", fill="x")
        self._header.pack_propagate(False)

        # Theme button (placeholder for now - wired up in Phase B)
        ctk.CTkButton(
            self._header, text="Theme", width=70, height=28,
            font=styles.FONT_DATE, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._on_theme_toggle
        ).pack(side="left", padx=12)

        # Centered title
        ctk.CTkLabel(self._header, text="RPG Battle Launcher", font=styles.FONT_TITLE, text_color=styles.THEME()["text_title"]).pack(side="left", fill="x", expand=True)

        # About button (placeholder for now - wired up in Phase D)
        ctk.CTkButton(
            self._header, text="About", width=70, height=28,
            font=styles.FONT_DATE, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=lambda: None
        ).pack(side="right", padx=12)

    def _build_content(self):
        """Central area for the news carousel (or About view)."""
        # background frame of the content area
        self._content_frame = ctk.CTkFrame(self, fg_color=styles.THEME()["bg"], corner_radius=0)
        self._content_frame.pack(fill="both", expand=True)

        # carousel container (rounded, centered, with margins)
        self._carousel = ctk.CTkFrame(self._content_frame, fg_color=styles.THEME()["panel"], corner_radius=12)
        self._carousel.pack(fill="both", expand=True, padx=24, pady=20)

        # Note: background label is created in _resize_carousel_bg method to avoid that the window has a provisional size

    def _resize_carousel_bg(self):
        """Resize the carousel background to fill its frame (called when layout is stable)."""
        self._carousel.update_idletasks()                 # update the carousel frame to get its actual size
        width = self._carousel.winfo_width()              # carousel width in pixels
        height = self._carousel.winfo_height()            # carousel height in pixels
        img = Image.open(launcher_background_path())      # get the launcher background image
        # Resize the carousel background image to fill its frame
        carousel_img = ctk.CTkImage(light_image=img, dark_image=img, size=(max(width, 10), max(height, 10)))

        # Create or configure the carousel background label
        if not hasattr(self, "_carousel_bg") or self._carousel_bg is None:
            self._carousel_bg = ctk.CTkLabel(self._carousel, image=carousel_img, text="")
            self._carousel_bg.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center")
        else:
            self._carousel_bg.configure(image=carousel_img)

    def _build_footer(self):
        """Bottom bar: versions, buttons and progress bar."""
        # Footer frame
        self._footer = ctk.CTkFrame(self, fg_color=styles.THEME()["panel"], corner_radius=0, height=60)
        self._footer.pack(side="bottom", fill="x")
        self._footer.pack_propagate(False)

        # Top row: labels + buttons
        row = ctk.CTkFrame(self._footer, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(8, 2))

        # Installed version
        installed = installed_version()
        self._lbl_installed = ctk.CTkLabel(row, text=f"Installed: {installed}" if installed else "Installed: —", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        self._lbl_installed.pack(side="left")

        # Remote version (filled later)
        self._lbl_latest = ctk.CTkLabel(row, text="Latest: ...", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        self._lbl_latest.pack(side="left", padx=(20, 0))

        # Check button
        self._btn_check = ctk.CTkButton(
            row, text="Check", width=70, height=28,
            font=styles.FONT_DATE, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._on_check_click
        )
        self._btn_check.pack(side="right", padx=(8, 0))

        # Play button
        self._btn_play = ctk.CTkButton(
            row, text="Play", width=90, height=28,
            font=styles.FONT_DATE, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._on_play_click
        )
        self._btn_play.pack(side="right", padx=(8, 0))

        # Download / Update button
        self._btn_download = ctk.CTkButton(
            row, text="Download", width=90, height=28,
            font=styles.FONT_DATE, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._on_download_click
        )
        self._btn_download.pack(side="right")

        # Initial state of the Play button (disabled if the game is not installed)
        if not is_game_installed():
            self._btn_play.configure(state="disabled")

        # Bottom row: progress bar (hidden at the start)
        self._progress = ctk.CTkProgressBar(self._footer, fg_color=styles.THEME()["border"], progress_color=styles.THEME()["accent"], height=6)
        self._progress.set(0)
        # Not packed here - shown only during download

    def _destroy_ui(self):
        """Destroy the three main bands so they can be rebuilt with the new theme."""
        # iterate over the main ui widgets and destroy them if they exist
        for name in ("_header", "_content_frame", "_footer"):
            widget = getattr(self, name, None)
            if widget is not None:
                widget.destroy()

        # set the carousel background to None to force it to be rebuilt
        self._carousel_bg = None

    def _on_theme_toggle(self):
        """Switch Light/Dark theme and rebuild the UI."""
        # switch theme
        styles.CURRENT_THEME = "Dark" if styles.CURRENT_THEME == "Light" else "Light"

        # keep ctk native mode in sync
        ctk.set_appearance_mode(styles.CURRENT_THEME)

        # persist the theme for next launch
        save_theme(styles.CURRENT_THEME)

        # set theme background color
        self.configure(fg_color=styles.THEME()["bg"])

        # destroy the ui
        self._destroy_ui()

        # rebuild the ui
        self._build_header()
        self._build_content()
        self._build_footer()

        # resize the carousel background
        self.after(0, self._resize_carousel_bg)

        # refresh the state of the ui
        self._refresh_state()

        # if news items exist, populate the news
        if self._news_items:
            self.after(0, lambda: self._populate_news(self._news_items))

    def _refresh_state(self):
        """Re-apply stored state to the (rebuilt) widgets."""
        # set the latest release version
        tag = self._latest_release.get("tag_name", "?") if self._latest_release else None
        self._lbl_latest.configure(text=f"Latest: {tag}" if tag else "Latest: —")

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
