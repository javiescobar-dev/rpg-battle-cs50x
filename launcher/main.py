# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Main launcher window and UI logic."""

import ctypes, time, sys, random, threading, ui_styles as styles, customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps

from ctypes import wintypes
from config import APP_NAME, APP_TITLE
from paths import installed_version, is_game_installed, launch_game, launcher_background_path, font_path, launcher_hero_path, title_font_path, theme_icon_path
from updater import fetch_latest_release, update
from news import get_news, get_image_path
from settings import load_theme, save_theme

class WINDOWPLACEMENT(ctypes.Structure):
    """Windows WINDOWPLACEMENT struct (not shipped with ctypes.wintypes)."""
    _fields_ = [
        ("length", ctypes.c_uint),          # ::UINT
        ("flags", ctypes.c_uint),           # ::UINT
        ("showCmd", ctypes.c_uint),         # ::UINT
        ("ptMinPosition", wintypes.POINT),  # ::POINT
        ("ptMaxPosition", wintypes.POINT),  # ::POINT
        ("rcNormalPosition", wintypes.RECT) # ::RECT
    ]

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
        self.configure(fg_color=styles.THEME()["bg"])     # set window background color
        self.configure(bg=styles.THEME()["bg"])
        # internal state
        self._latest_release = None                       # stores the latest release from server
        self._news_items = []                             # stores the news items once loaded
        self._carousel_index = 0                          # which news slide is active
        self._carousel_bg = None                          # stores the carousel background image
        self._carousel_moving = False                     # stores whether the carousel is moving
        self._carousel_anim_timer = None                  # stores the carousel animation timer ID
        self._view = "news"                               # which view is active: "news" or "about"
        self._hero_sprite = None                          # stores the hero sprite for the download animation
        self._hero_frames = []                            # stores the hero animation frames
        self._hero_frame = 0                              # stores the current hero animation frame index
        self._hero_timer = None                           # stores the hero animation timer ID
        self._theme_busy = False                          # stores whether the theme is changing
        self._last_theme_toggle = 0.0                     # stores the time of the last theme toggle (used to prevent rapid toggling)
        self._news_images = {}                            # stores the loaded news images by image field
        self._images_loading = set()                      # stores the news image fields currently downloading
        self._drag_x = 0                                  # stores the grab offset of the header drag (x)
        self._drag_y = 0                                  # stores the grab offset of the header drag (y)
        self._win_btns = []                               # window control buttons (close/minimize)
        self._about_widgets = None                        # widgets of the About view
        self._lbl_no_news = None                          # "No news available." label
        self._wndproc_cb = None                           # stores the subclass callback while the window is alive

        # bind the Map event to the _on_window_map method (call _on_window_map when the window is mapped)
        self.bind("<Map>", self._on_window_map)

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
        # Show the window frameless: strip the title bar while hidden,
        # then size the window with the final (frameless) styles
        self._install_hidden_titlebar()           # strip the native title bar while still hidden
        self.geometry(f"{styles.WINDOW_WIDTH}x{styles.WINDOW_HEIGHT}")  # re-apply the exact window size
        self.minsize(0, 0)                        # set min size to (0, 0) wide non-equal min/max: cancel CTk's fixed-size hints so Tk keeps WS_THICKFRAME (clamp comes later)
        self.maxsize(10000, 10000)                # set max size to (10000, 10000) wide non-equal min/max: cancel CTk's fixed-size hints so Tk keeps WS_THICKFRAME (clamp comes later)
        self.update_idletasks()                   # process any pending geometry updates
        self.deiconify()                          # show the window
        self.lift()                               # bring the window to the front
        self.focus_force()                        # force the window to be focused
        self.after(80, self.focus_force)
        self.attributes("-topmost", True)
        self.after(150, lambda: self.attributes("-topmost", False))
        self.update_idletasks()                   # process any pending geometry updates (now the layout is truly settled)
        self._ensure_client_size()                # make the drawable area exactly the designed size
        self.update_idletasks()                   # process the corrected size
        self._apply_rounded_corners()             # round the corners once the window is visible
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
            self._lbl_no_news = ctk.CTkLabel(self._content_frame, text="No news available.", font=styles.FONT_BODY, text_color=styles.THEME()["text_date"])
            self._lbl_no_news.pack(pady=40)
            return

        # show the first slide
        self._show_slide(self._carousel_index)

        # preload the news images in the background
        for i in range(len(items)):
            self._ensure_image(i)

    def _show_slide(self, index):
        """Mark the active slide and re-render the carousel image."""
        # check if the news items are loaded, if not, return
        if not self._news_items:
            return

        # get the number of news items
        n = len(self._news_items)
        if n == 0:
            return

        # set the active slide index
        self._carousel_index = index % n          # circular safety

        # re-render background + stripe + text
        self._resize_carousel_bg()

    def _carousel_next(self):
        """Go to next news slide."""
        self._animate_to(self._carousel_index + 1, "right")

    def _carousel_prev(self):
        """Go to previous news slide."""
        self._animate_to(self._carousel_index - 1, "left")

    def _animate_to(self, target_index: int, direction: str):
        """Animate to the given index."""
        # check if the news items are loaded, if not, return
        if not self._news_items:
            return

        # get the number of news items
        n = len(self._news_items)
        if n == 0:
            return

        # prevent re-animating to the same slide
        if target_index % n == self._carousel_index:
            return

        # If there's no previous image, snap directly
        if not self._carousel_bg:
            self._carousel_index = target_index % n
            self._resize_carousel_bg()
            self._carousel_moving = False
            return

        # get old and new index
        old_index = self._carousel_index
        new_index = target_index % n

        # set the active slide index
        self._carousel_index = new_index

        # save the destination for _on_image_ready
        self._anim_target = new_index

        # render old and new slide
        old_img = self._render_slide(old_index, False)
        new_img = self._render_slide(new_index, False)
        self._carousel_anim_final_img = self._render_slide(new_index, True)

        old_img_render = ctk.CTkImage(light_image=old_img, dark_image=old_img, size=old_img.size)
        new_img_render = ctk.CTkImage(light_image=new_img, dark_image=new_img, size=new_img.size)

        # destroy old carousel background
        self._carousel_bg.destroy()

        # create labels
        old_lbl = ctk.CTkLabel(self._carousel, image=old_img_render, text="")
        new_lbl = ctk.CTkLabel(self._carousel, image=new_img_render, text="")

        # place labels
        old_lbl.place(relwidth=1, relheight=1, x=0, y=0, anchor="nw")  # old label starts at the left side
        # set new label position based on direction
        width = self._carousel.winfo_width()
        if direction == "left":
            new_lbl.place(relwidth=1, relheight=1, x=-width, y=0, anchor="nw")
        elif direction == "right":
            new_lbl.place(relwidth=1, relheight=1, x=width, y=0, anchor="nw")

        # set animation variables
        steps = 15
        self._anim_old = old_lbl
        self._anim_new = new_lbl
        self._anim_sign = 1 if direction == "right" else -1
        self._anim_delta = width / steps
        self._anim_progress = 0.0
        self._carousel_moving = True

        # start slide animation timer
        self._carousel_anim_timer = self.after(20, self._slide_step)

    def _slide_step(self):
        # increase the counter
        self._anim_progress += self._anim_delta

        width = self._carousel.winfo_width()
        
        # check if animation is finished
        if self._anim_progress >= width:
            # create final image render
            final_img_render = ctk.CTkImage(light_image=self._carousel_anim_final_img, dark_image=self._carousel_anim_final_img, size=self._carousel_anim_final_img.size)
            self._anim_new.configure(image=final_img_render)

            # destroy old slide
            self._anim_old.destroy()
            # set new slide
            self._carousel_bg = self._anim_new
            self._carousel_bg.place(relwidth=1, relheight=1, x=0, y=0, anchor="nw")
            self._carousel_bg.bind("<Button-1>", self._on_carousel_click)
            self._carousel_moving = False                     # unlock clicks
            return                                            # stop animation

        # If the animation is not finished, move a little bit and reprogram
        sign = self._anim_sign
        progress = self._anim_progress

        # move old and new slide
        self._anim_old.place(relwidth=1, relheight=1, x=-sign * progress, y=0, anchor="nw")           # leave
        self._anim_new.place(relwidth=1, relheight=1, x=sign * (width - progress), y=0, anchor="nw")  # enter

        # schedule next frame
        self._carousel_anim_timer = self.after(20, self._slide_step)   

    def _build_header(self):
        """Top bar with title and placeholder buttons."""

        # Top bar frame (full width, fixed height)
        self._header = ctk.CTkFrame(self, fg_color=styles.THEME()["panel"], corner_radius=0, height=styles.HEADER_HEIGHT)
        self._header.pack(side="top", fill="x")
        self._header.pack_propagate(False)

        # About label
        self._lbl_about = ctk.CTkLabel(self._header, text="About", font=styles.FONT_BOLD, text_color=styles.THEME()["text_title"], cursor="hand2")
        self._lbl_about.pack(side="left", padx=(12, 4))
        self._lbl_about.bind("<Button-1>", lambda e: self._show_about())

        # Theme slider
        icon_name = styles.ICONS["theme_light"] if styles.CURRENT_THEME == "Dark" else styles.ICONS["theme_dark"]
        icon_img = Image.open(theme_icon_path(icon_name))
        icon_img = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(24, 24))
        self._btn_theme = ctk.CTkButton(self._header, text="", image=icon_img, width=24, height=24, fg_color="transparent", hover=False, command=self._on_theme_toggle)
        self._btn_theme.pack(side="left", padx=4)

        # Window controls (frameless): close and minimize, flush in the top-right corner
        self._win_btns = []  # store window control buttons for theme swap (recoloring)
        gap = 8
        for i, (name, cmd) in enumerate(((styles.ICONS["close"], self._on_close_click), (styles.ICONS["minimize"], self._on_minimize_click))):
            icon_img = Image.open(theme_icon_path(name))
            icon_img = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(24, 24))
            btn = ctk.CTkButton(self._header, text="", image=icon_img, width=28, height=28, corner_radius=0, fg_color="transparent", hover_color=styles.THEME()["border"], command=cmd)
            btn.place(relx=1.0, anchor="ne", x=-(6 + i * (28 + gap)), y=4)
            self._win_btns.append(btn)

        # Centered title
        self._lbl_title = ctk.CTkLabel(self._header, text="", image=self._render_title_image())
        self._lbl_title.place(relx=0.5, rely=0.5, anchor="center")

        # Header drag (frameless window): grab on press, move while dragging
        self._header.bind("<Button-1>", self._on_drag_start)
        self._header.bind("<B1-Motion>", self._on_drag_move)

    def _on_minimize_click(self):
        """Minimize natively (keeps the OS transition)."""
        self.iconify()

    def _on_close_click(self):
        """Close the application."""
        self.destroy()

    def _on_drag_start(self, event):
        """Record the grab offset between the mouse and the window origin."""
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _on_drag_move(self, event):
        """Move the window keeping the grab offset fixed under the mouse."""
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        if sys.platform == "win32":
            # position-only move: never touch the size and keep the window active
            SWP_NOSIZE, SWP_NOZORDER, SWP_NOACTIVATE = 0x0001, 0x0004, 0x0010

            # Get the OS handle of the window
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

            # Move the window
            ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
        else:
            self.geometry(f"+{x}+{y}")

    def _ensure_client_size(self) -> bool:
        """Force the drawable (client) area to the exact designed size.
        A managed window can keep a few invisible frame pixels that shrink the client area, trimming the right edge of the UI."""
        if sys.platform != "win32":
            return False

        # Get the OS handle of the window
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        # measure the window rectangle and the drawn (client) rectangle
        client, outer = wintypes.RECT(), wintypes.RECT()
        ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(client))
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(outer))

        # actual size of the frame
        cur_w = outer.right - outer.left
        cur_h = outer.bottom - outer.top

        # invisible frame leftover = total window rect minus the drawable rect
        dx = cur_w - (client.right - client.left)
        dy = cur_h - (client.bottom - client.top)

        # size that the frame should have to make the client exact
        want_w = styles.WINDOW_WIDTH + dx
        want_h = styles.WINDOW_HEIGHT + dy

        # if it is already correct, do nothing (ends the event loop)
        if cur_w == want_w and cur_h == want_h:
            return False

        # resize the window to the correct size
        self.geometry(f"{want_w}x{want_h}")
        return True

    def _apply_rounded_corners(self):
        """Round the frameless window corners via the Windows region API."""
        return
        if sys.platform != "win32":
            return
        from ctypes import wintypes

        radius = styles.WINDOW_CORNER_RADIUS

        # Get the OS handle of the window
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        # measure the real window rectangle (it can include an invisible frame)
        outer = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(outer))
        width = outer.right - outer.left
        height = outer.bottom - outer.top

        # Create a rounded region with the specified radius
        region = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, width + 1, height + 1, radius * 2, radius * 2)

        # Set the window region to the rounded rectangle
        ctypes.windll.user32.SetWindowRgn(hwnd, region, True)

    def _on_window_map(self, event=None):
        """Apply rounded corners immediately when the window is mapped."""
        if sys.platform != "win32" or self.state() != "normal":
            return
        self._apply_rounded_corners()

    def _install_hidden_titlebar(self):
        """Installs a subclass to hide the native title bar while keeping the window fully managed by the OS."""
        if sys.platform != "win32":
            return

        # Get the OS handle of the window
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        # constants
        WM_NCCALCSIZE = 0x0083                  # message: "measure the non-client area"
        comctl = ctypes.WinDLL("comctl32")      # ComCtl32 provides the subclass functions

        # callback definition
        SUBCLASSPROC = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,                   # LRESULT
            wintypes.HWND,                      # hwnd
            wintypes.UINT,                      # uMsg
            wintypes.WPARAM,                    # wParam
            wintypes.LPARAM,                    # lParam
            ctypes.c_size_t,                    # uIdSubclass
            ctypes.c_size_t                     # dwRefData
        )

        # comctl32 function signatures
        comctl.SetWindowSubclass.argtypes = [wintypes.HWND, SUBCLASSPROC, ctypes.c_size_t, ctypes.c_size_t]
        comctl.SetWindowSubclass.restype  = ctypes.c_bool
        comctl.DefSubclassProc.argtypes  = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM, ctypes.c_size_t, ctypes.c_size_t]
        comctl.DefSubclassProc.restype   = ctypes.c_ssize_t

        # callback to process messages
        @SUBCLASSPROC
        def _wnd_proc(hwnd, msg, wparam, lparam, u_id, ref_data):
            # If the message is WM_NCCALCSIZE and the wParam is true, then the window is being resized
            if msg == WM_NCCALCSIZE and wparam:
                return 0
            # Otherwise, call the default subclass procedure
            return comctl.DefSubclassProc(hwnd, msg, wparam, lparam, u_id, ref_data)

        # store callback and register it to the window
        self._wndproc_cb = _wnd_proc
        comctl.SetWindowSubclass(hwnd, self._wndproc_cb, 1, 0)

        # ask Windows to re-apply the changed window styles
        SWP_NOSIZE       = 0x0001                  # don't change the size
        SWP_NOMOVE       = 0x0002                  # don't move the window
        SWP_NOZORDER     = 0x0004                  # don't change the z-order
        SWP_FRAMECHANGED = 0x0020                  # re-read the just-applied window styles
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

    def _build_content(self):
        """Central area for the news carousel (or About view)."""

        # background frame of the content area
        self._content_frame = ctk.CTkFrame(self, fg_color=styles.THEME()["bg"], corner_radius=0)
        self._content_frame.pack(fill="both", expand=True)

        # carousel container (rounded, centered, with margins)
        self._build_carousel()

        # Note: background label is created in _resize_carousel_bg method to avoid that the window has a provisional size

    def _destroy_content(self):
        """Destroy the widgets inside the content area."""
        # destroy the widgets inside the content area (children widgets)
        for child in self._content_frame.winfo_children():
            child.destroy()

        # reset the carousel background after destroying the carousel
        self._carousel_bg = None

        # reset the carousel also
        self._carousel = None

        # reset the animation timer
        if self._carousel_anim_timer:
            self.after_cancel(self._carousel_anim_timer)
            self._carousel_anim_timer = None

        # reset the carousel moving state
        self._carousel_moving = False

    def _build_carousel(self):
        """Area to show news."""
        # create the carousel frame
        self._carousel = ctk.CTkFrame(self._content_frame, fg_color=styles.THEME()["panel"], corner_radius=0)
        # pack the carousel frame
        self._carousel.pack(fill="both", expand=True, padx=0, pady=0)

    def _render_slide(self, index: int, include_ui: bool = True) -> Image:
        """Render the carousel slide with the given index."""
        # update the carousel frame to get its actual size (only if it is not already done)
        if self._carousel.winfo_width() < 10 or self._carousel.winfo_height() < 10:
            self._carousel.update_idletasks()
        # carousel width in pixels
        width = self._carousel.winfo_width()
        # carousel height in pixels
        height = self._carousel.winfo_height()
        # make sure the size is at least 10x10
        size = (max(width, 10), max(height, 10))

        # news photo if it is already loaded
        item = self._news_items[index] if 0 <= index < len(self._news_items) else None
        img_field = item.get("image") if item else None
        news_img = self._news_images.get(img_field) if img_field else None

        # if the news has an image but it is not loaded yet, schedule it
        if img_field and img_field not in self._news_images:
            self._ensure_image(index)

        # build the base background
        if news_img is not None:
            img = ImageOps.fit(news_img, size).convert("RGBA")     # photo: crop to fill
        else:
            try:
                # default background image
                img = Image.open(launcher_background_path()).convert("RGBA").resize(size)
            except Exception:
                # no background image: flat fallback filled with the theme background color
                img = Image.new("RGBA", size, styles.THEME()["bg"] + "FF")  # flat, no baked UI
                return img.convert("RGB")

        # draw a semi-transparent bar (title region + body region)
        bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(bar)
        top, bottom = int(height * 0.70), int(height * 0.96)
        draw.rectangle([0, top, width, bottom], fill=(8, 8, 16, 90))

        # overlay stripe onto background
        img = Image.alpha_composite(img, bar)

        # set the news text and draw navigation buttons and dots if exists news and index is valid (only if include_ui is true)
        if include_ui and self._news_items and 0 <= index < len(self._news_items):
            # get the news item
            item = self._news_items[index]
            # draw the news text
            self._draw_news_text(img, item.get("title", ""), item.get("body", ""), width, height)
            # draw navigation buttons and dots
            self._draw_nav(img, width, height, index)

        # convert the image to RGB
        return img.convert("RGB")

    def _display_render(self, img):
        """Display the rendered slide in the carousel."""
        # Resize the carousel background image to fill its frame
        carousel_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

        # Create the carousel background label, if exists destroy it first
        if self._carousel_bg is not None:
            self._carousel_bg.destroy()
        self._carousel_bg = ctk.CTkLabel(self._carousel, image=carousel_img, text="")
        self._carousel_bg.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center")

        # bind the carousel click event to the on_carousel_click method
        self._carousel_bg.bind("<Button-1>", self._on_carousel_click)

    def _resize_carousel_bg(self):
        """Resize the carousel background to fill its frame (called when layout is stable)."""
        img = self._render_slide(self._carousel_index)
        self._display_render(img)

    def _ensure_image(self, index: int) -> None:
        """Schedule loading the news image for the given slide (UI thread)."""
        # get the news item
        item = self._news_items[index] if 0 <= index < len(self._news_items) else None
        # get the image field
        img_field = item.get("image") if item else None
        # if the image field is not found or the image is already loaded or is loading, return
        if not img_field or img_field in self._news_images or img_field in self._images_loading:
            return
        # add the image field to the loading set
        self._images_loading.add(img_field)
        # start loading the image in a separate thread
        threading.Thread(target=self._load_image, args=(index, img_field), daemon=True).start()

    def _load_image(self, index: int, img_field: str) -> None:
        """Load the image in a background thread (network + disk)."""
        # get the image path
        path = get_image_path(img_field)
        img = None
        if path:
            # try to open the image
            try:
                img = Image.open(path).convert("RGB")
            except Exception:
                img = None
        # call the on_image_ready method in the UI thread
        self.after(0, lambda: self._on_image_ready(index, img_field, img))

    def _on_image_ready(self, index: int, img_field: str, img) -> None:
        """Store the loaded image and refresh the slide if needed (UI thread)."""
        # remove the image field from the loading set
        self._images_loading.discard(img_field)
        # store the loaded image
        self._news_images[img_field] = img   # None means it failed; do not retry
        # if an animation heads to this slide, update its final image
        if self._carousel_moving and self._anim_target == index:
            self._carousel_anim_final_img = self._render_slide(index, True)
        # if it is the active slide, re-render it
        if (not self._carousel_moving and self._view == "news" and self._carousel is not None and self._carousel_index == index):
            self._resize_carousel_bg()

    def _draw_news_text(self, img, title, body, width, height):
        """Draw the slide title and body onto the carousel image."""

        # Resolve cross-platform font paths
        title_path = font_path(True)  # Bold
        body_path  = font_path(False) # Regular

        # Create the fonts
        title_font = (ImageFont.truetype(str(title_path), 24) if title_path else ImageFont.load_default(size=24))
        body_font  = (ImageFont.truetype(str(body_path), 15) if body_path else ImageFont.load_default(size=15))

        # Draw the title and body
        draw = ImageDraw.Draw(img)
        cx = width // 2
        max_text_w = int(width * 0.8)

        # Centered title
        if title:
            draw.text((cx, int(height*0.74)), title, font=title_font, fill=(255, 255, 255, 255), anchor="mm")

        # body: wrap by words and center each line
        if body:
            # wrap text by words
            lines = []
            current = ""
            for word in body.split():
                trial = (current + " " + word).strip()
                if draw.textbbox((0, 0), trial, font=body_font)[2] <= max_text_w:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            # Add the last word
            if current:
                lines.append(current)

            # Centered body
            y = int(height * 0.82)

            # Draw the body
            for line in lines:
                draw.text((cx, y), line, font=body_font, fill=(230, 230, 230, 255), anchor="mm")
                y += 18

    def _draw_nav(self, img, width, height, index: int):
        """Draw arrow buttons and navigation dots onto the carousel image."""
        n = len(self._news_items)
        if n <= 1:          # nothing to navigate
            return

        # arrows
        draw = ImageDraw.Draw(img)
        accent = styles.THEME()["accent"]
        inactive = styles.THEME()["text_date"]
        cy = int(height * 0.5)

        # left arrow ‹ (triangle pointing left), centered vertically
        ax = int(width * 0.03)
        draw.polygon([(ax - 8, cy), (ax + 8, cy - 16), (ax + 8, cy + 16)], fill=accent)
        # right arrow › (triangle pointing right), centered vertically
        bx = int(width * 0.97)
        draw.polygon([(bx + 8, cy), (bx - 8, cy - 16), (bx - 8, cy + 16)], fill=accent)

        # navigation dots (circle per slide), centered at the bottom
        gap = 18
        dy = int(height * 0.95)
        self._dot_centers = []
        # iterate over the number of news items
        for i in range(n):
            # calculate the x coordinate of the dot
            dx = width // 2 + int((i - (n - 1) / 2) * gap)
            # set the color of the dot
            color = accent if i == index else inactive
            # draw the dot
            draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=color)
            # append the dot center to the list
            self._dot_centers.append((dx, dy))

    def _on_carousel_click(self, event):
        """Handle a click on the carousel image: prev/next arrows or a specific dot."""
        n = len(self._news_items)
        if n <= 1:
            return                      # nothing to navigate

        # if carousel is moving, return
        if self._carousel_moving:
            return

        # get carousel size
        width = self._carousel.winfo_width()
        height = self._carousel.winfo_height()

        # left arrow zone (0% to 6% of the carousel width)
        if event.x < width * 0.06:
            self._carousel_prev()
            return

        # right arrow zone (94% to 100% of the carousel width)
        if event.x > width * 0.94:
            self._carousel_next()
            return

        # dots zone (bottom bar): pick the closest dot to the click
        if event.y > height * 0.90 and self._dot_centers:
            best = min(range(n), key=lambda i: abs(event.x - self._dot_centers[i][0]))
            direction = "right" if best > self._carousel_index else "left"
            self._animate_to(best, direction)

    def _show_about(self):
        """Switch the content area to the About view."""
        self._view = "about"
        self._destroy_content()
        self._build_about()

    def _show_news(self):
        """Switch the content area back to the news carousel."""
        self._view = "news"
        self._destroy_content()
        self._build_carousel()
        # restore the active slide (self._carousel_index keeps it) with a delay of 0 ms to avoid that the carousel is not fully built
        if self._news_items:
            self.after(0, lambda: self._populate_news(self._news_items))

    def _build_about(self):
        """Build the About view."""
        # destroy the content frame
        self._destroy_content()
        # get content frame to build the About view inside
        frame = ctk.CTkFrame(self._content_frame, fg_color=styles.THEME()["bg"], corner_radius=0)
        frame.pack(fill="both", expand=True)  # fill the content frame and expand to fill the available space
        # title
        title = ctk.CTkLabel(frame, text=APP_NAME, font=styles.FONT_TITLE, text_color=styles.THEME()["text_title"])
        title.pack(pady=(40, 8))
        # body
        body = ctk.CTkLabel(frame, text="RPG Battle is a turn-based battle game built with Pygame and a desktop launcher built with CustomTkinter. It is the final project of CS50x.",
                                    font=styles.FONT_BODY, text_color=styles.THEME()["text_body"], wraplength=600, justify="center")
        body.pack(pady=8)
        # subtitle: developed by
        author = ctk.CTkLabel(frame, text="Developed by Javi Escobar Fernández", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        author.pack(pady=8)
        # subtitle: CS50x Final Project
        project = ctk.CTkLabel(frame, text="CS50x Final Project", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        project.pack(pady=8)
        # back button
        back_btn = ctk.CTkButton(
            frame, text="Back", width=70, height=28,
            font=styles.FONT_BODY, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._show_news
        )
        back_btn.pack(pady=16)

        # store widgets for theme swap
        self._about_widgets = {
            "frame": frame,
            "title": title,
            "body": body,
            "author": author,
            "project": project,
            "back": back_btn,
        }

    def _render_title_image(self):
        """Render the header title with the game font and return a CTkImage."""
        font = None
        # try to load the title font (finalf.ttf)
        try:
            font = ImageFont.truetype(str(title_font_path()), styles.TITLE_FONT_SIZE)
        except Exception:
            # if the title font is not found, try to load the system bold font
            sys_font = font_path(True)
            if sys_font:
                font = ImageFont.truetype(str(sys_font), styles.TITLE_FONT_SIZE)
        # if the system bold font is not found, use the default font
        if font is None:
            font = ImageFont.load_default(size=styles.TITLE_FONT_SIZE)

        # define text to draw
        text = APP_TITLE
        # create a dummy image and draw the text on it
        draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bbox = draw.textbbox((0, 0), text, font=font)
        # calculate the size of the text
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # bar: wider than the text, centered with it
        margin = 8
        # calculate the width of the bar
        bar_w = w + styles.TITLE_BAR_EXTRA_W
        # calculate the width of the canvas
        canvas_w = bar_w + 2 * margin
        # calculate the height of the canvas
        canvas_h = margin + h + styles.TITLE_BAR_GAP + styles.TITLE_BAR_H + margin

        # create the title image
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # text centered over the bar (offset bbox by -bbox to place it exactly)
        draw.text((margin + (bar_w - w) // 2 - bbox[0], margin - bbox[1]),
                  text, font=font, fill=styles.THEME()["text_title"])
        # underline bar below the text, same color as the title
        bar_y = margin + h + styles.TITLE_BAR_GAP
        draw.rounded_rectangle(
            [margin, bar_y, margin + bar_w, bar_y + styles.TITLE_BAR_H],
            radius=styles.TITLE_BAR_H / 2, fill=styles.THEME()["text_title"])
        # return the image as a CTkImage
        return ctk.CTkImage(light_image=img, dark_image=img, size=(canvas_w, canvas_h))

    def _build_footer(self):
        """Build the footer, the bottom bar of the launcher."""

        # Footer frame
        self._footer = ctk.CTkFrame(self, fg_color=styles.THEME()["panel"], corner_radius=0, height=styles.FOOTER_HEIGHT)
        self._footer.pack(side="bottom", fill="x")
        self._footer.pack_propagate(False)

        # Top zone: progress bar + sprite (dynamic, only during download)
        self._top_zone = ctk.CTkFrame(self._footer, fg_color="transparent")
        self._top_zone.pack(side="top", fill="x")
        # not propagating the size of children
        self._top_zone.pack_propagate(False)
        # set height to 0, it will be increased when the download starts
        self._top_zone.configure(height=0)

        # progress bar (hidden at the start)
        self._progress = ctk.CTkProgressBar(self._top_zone, fg_color=styles.THEME()["border"], progress_color=styles.THEME()["accent"], height=6)
        self._progress.set(0)
        # Not packed here - shown only during download

        # Bottom zone: versions + buttons (always visible, anchored to bottom)
        self._row = ctk.CTkFrame(self._footer, fg_color="transparent")
        self._row.pack(side="bottom", fill="x", padx=16, pady=(0, 8))

        # Installed version
        installed = installed_version()
        self._lbl_installed = ctk.CTkLabel(self._row, text=f"Installed: {installed}" if installed else "Installed: —", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        self._lbl_installed.pack(side="left")

        # Remote version (filled later)
        self._lbl_latest = ctk.CTkLabel(self._row, text="Latest: ...", font=styles.FONT_DATE, text_color=styles.THEME()["text_body"])
        self._lbl_latest.pack(side="left", padx=(20, 0))

        # Check button
        self._btn_check = ctk.CTkButton(
            self._row, text="Check", width=70, height=styles.BUTTON_HEIGHT, border_spacing=0, border_width=0, corner_radius=6,
            font=styles.FONT_BUTTON, fg_color=styles.THEME()["accent"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["button_text"],
            command=self._on_check_click
        )
        self._btn_check.pack(side="right", padx=(8, 0))

        # Play button
        self._btn_play = ctk.CTkButton(
            self._row, text="Play", width=90, height=styles.BUTTON_HEIGHT, border_spacing=0, border_width=0, corner_radius=6,
            font=styles.FONT_BUTTON, fg_color=styles.THEME()["play_button"],
            hover_color=styles.THEME()["play_button_hover"], text_color=styles.THEME()["button_text"],
            command=self._on_play_click
        )
        self._btn_play.pack(side="right", padx=(8, 0))

        # Download / Update button
        self._btn_download = ctk.CTkButton(
            self._row, text="Download", width=90, height=styles.BUTTON_HEIGHT, border_spacing=0, border_width=1, corner_radius=6, border_color=styles.THEME()["accent"],
            font=styles.FONT_BUTTON, fg_color=styles.THEME()["panel"],
            hover_color=styles.THEME()["hover"], text_color=styles.THEME()["accent"],
            command=self._on_download_click
        )
        self._btn_download.pack(side="right")
        self._btn_download.bind("<Enter>", lambda event: self._btn_download.configure(text_color=styles.THEME()["button_text"],fg_color=styles.THEME()["accent"]))
        self._btn_download.bind("<Leave>", lambda event: self._btn_download.configure(text_color=styles.THEME()["accent"],fg_color=styles.THEME()["panel"]))

        # Initial state of the Play button (disabled if the game is not installed)
        if not is_game_installed():
            self._btn_play.configure(state="disabled")

    def _on_theme_toggle(self):
        """Switch Light/Dark theme by recoloring the existing widgets in place."""
        # protect swicht theme if button theme is busy
        if self._theme_busy:
            return

        # small delay to prevent spam
        now = time.monotonic()
        if now - self._last_theme_toggle < 0.8:
            return
        self._last_theme_toggle = now

        # set flag to prevent concurrent theme switch
        self._theme_busy = True
        try:
            # switch theme
            styles.CURRENT_THEME = "Dark" if styles.CURRENT_THEME == "Light" else "Light"

            # persist the theme for next launch
            save_theme(styles.CURRENT_THEME)

            # apply the new theme
            self._apply_theme()
        finally:
            # set the flag to False so that the theme can be switched again
            self._theme_busy = False

    def _apply_theme(self):
        """Re-color the whole UI in place with the new theme (no rebuild, no flicker)."""
        theme = styles.THEME()
        # apply theme to header
        self._recolor_header()
        # apply theme to content
        self._recolor_content()
        # apply theme to footer
        self._recolor_footer()
        # set the background color
        self.configure(fg_color=theme["bg"])
        self.configure(bg=theme["bg"])
        # update the UI
        self.update_idletasks()

    def _recolor_header(self):
        """Re-color the header in place with the new theme."""
        theme = styles.THEME()
        # set the header background color
        self._header.configure(fg_color=theme["panel"])
        # set the about label text color
        self._lbl_about.configure(text_color=theme["text_title"])
        # set the window buttons hover color
        for btn in self._win_btns:
            btn.configure(hover_color=theme["border"])
        # theme button shows the icon of the OTHER theme
        icon_name = styles.ICONS["theme_light"] if styles.CURRENT_THEME == "Dark" else styles.ICONS["theme_dark"]
        icon = Image.open(theme_icon_path(icon_name))
        icon = ctk.CTkImage(light_image=icon, dark_image=icon, size=(24, 24))
        self._btn_theme.configure(image=icon)
        # title re-rendered with the new text color
        self._lbl_title.configure(image=self._render_title_image())

    def _recolor_content(self):
        """Re-color the content in place with the new theme."""
        theme = styles.THEME()
        # set the content frame background color
        self._content_frame.configure(fg_color=theme["bg"])
        # set the carousel background color
        if self._carousel is not None:
            self._carousel.configure(fg_color=theme["panel"])
        # set the about label text color
        if self._view == "about":
            self._recolor_about()
        # set the news items background color
        elif self._news_items:
            self._resize_carousel_bg()
        # set the no news label text color
        elif self._lbl_no_news is not None and self._lbl_no_news.winfo_exists():
            self._lbl_no_news.configure(text_color=theme["text_date"])

    def _recolor_about(self):
        """Re-color the about widgets in place with the new theme."""
        theme = styles.THEME()
        widgets = self._about_widgets
        # set the about frame background color
        widgets["frame"].configure(fg_color=theme["bg"])
        # set the about label text color
        widgets["title"].configure(text_color=theme["text_title"])
        # set the about body text color
        for lbl in (widgets["body"], widgets["author"], widgets["project"]):
            lbl.configure(text_color=theme["text_body"])
        # set the about back button color
        widgets["back"].configure(fg_color=theme["accent"], hover_color=theme["hover"], text_color=theme["button_text"])

    def _recolor_footer(self):
        """Re-color the footer in place with the new theme."""
        theme = styles.THEME()
        # set the footer background color
        self._footer.configure(fg_color=theme["panel"])
        # set the progress bar background color
        self._progress.configure(fg_color=theme["border"], progress_color=theme["accent"])
        # set the installed label text color
        self._lbl_installed.configure(text_color=theme["text_body"])
        # set the latest release label text color
        self._lbl_latest.configure(text_color=theme["text_body"])
        # set the check button color
        self._btn_check.configure(fg_color=theme["accent"], hover_color=theme["hover"], text_color=theme["button_text"])
        # set the play button color
        self._btn_play.configure(fg_color=theme["play_button"], hover_color=theme["play_button_hover"], text_color=theme["button_text"])
        # set the download button color
        self._btn_download.configure(border_color=theme["accent"], fg_color=theme["panel"], hover_color=theme["hover"], text_color=theme["accent"])

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
        self._btn_theme.configure(state="disabled")

        # show progress bar and set height of top zone
        self._top_zone.configure(height=styles.FOOTER_TOP_HEIGHT)
        self._progress.set(0)
        self._progress.pack(side="bottom", fill="x", padx=16, pady=(12, 4))

        # clear hero frames if they exist
        self._hero_frames = []

        # select a random frame of the hero sprites
        frame = random.randint(1, 8)
        try:
            # Load the hero image sprite sheet and convert it to RGBA (transparency)
            sheet = Image.open(launcher_hero_path(frame)).convert("RGBA")

            # Height chosen for the sprite
            hero_h = 46

            # Crop the hero sprite into frames
            for frame in range(3):
                col = 2 * 3 + frame        # pose_idx=2 (flee) * 3 + frame
                x = col * 96
                new_frame = sheet.crop((x, 0, x + 96, 96))
                # Resize to a fixed height (e.g. 36 px) maintaining the proportion
                hero_w = int(new_frame.width * hero_h / new_frame.height)  # proportional
                new_frame = new_frame.resize((hero_w, hero_h))
                # Convert to an object that Tkinter can draw
                ctk_img = ctk.CTkImage(light_image=new_frame, dark_image=new_frame, size=(hero_w, hero_h))
                self._hero_frames.append(ctk_img)

            # Force the layout to have real size
            self.update_idletasks()

            # Calculate Y coordinate for the hero sprite (centered above the progress bar)
            TOP_H = self._top_zone.winfo_height()   # bar height
            bar_y = TOP_H - 6 - 12                  # bar at bottom (bar_h=6, pady bottom=12)
            y = bar_y - hero_h // 2 + 6             # vertical center of the sprite just above the bar

            # Create the label and place it with place (on the left)
            self._hero_sprite = ctk.CTkLabel(self._top_zone, image=self._hero_frames[0], text="", fg_color="transparent", bg_color="transparent")
            self._hero_sprite.place(x=16, y=y, anchor="w")

            # create timer to cycle hero sprite
            self._hero_timer = self.after(100, self._cycle_hero)
        except Exception:
            self._hero_sprite = None  # if the asset fails, only the progress bar works

        # thread to download the game
        def _do_update():
            # progress callback
            def on_progress(fraction):
                self.after(0, lambda: self._progress.set(fraction))   # move the progress bar
                self.after(0, lambda: self._update_sprite(fraction))  # move the hero sprite

            # download the game
            success = update(tag, progress_callback=on_progress)

            # finish download (after GUI is ready)
            def _finish():
                # hide progress bar
                self._progress.pack_forget()
                # hide top zone
                self._top_zone.configure(height=0)

                # hide hero sprite
                if self._hero_sprite is not None:
                    self._hero_sprite.place_forget()
                    self._hero_sprite = None

                # stop timer to cycle hero sprite
                if self._hero_timer is not None:
                    self.after_cancel(self._hero_timer)
                    self._hero_timer = None

                # restore buttons
                self._btn_download.configure(state="normal", text="Download")
                self._btn_check.configure(state="normal")
                self._btn_theme.configure(state="normal")

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

    def _update_sprite(self, fraction):
        """Update the hero sprite position (runs in a background thread)."""
        # move the progress bar (as it already is)
        self._progress.set(fraction)
        # no sprite, nothing to move
        if self._hero_sprite is None:
            return
        # travel space: from left margin to right (leaving room for the hero)
        travel = self._footer.winfo_width() - 32 - self._hero_sprite.winfo_width()
        x = 16 + fraction * travel  # 0.0 -> left, 1.0 -> right
        self._hero_sprite.place(x=x)  # move (and it was already fixed when created)


    def _cycle_hero(self):
        self._hero_frame = (self._hero_frame + 1) % 3
        self._hero_sprite.configure(image=self._hero_frames[self._hero_frame])
        self._hero_timer = self.after(100, self._cycle_hero)


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
