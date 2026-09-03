# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Path configuration and helpers for the launcher."""

from pathlib import Path
import platformdirs, subprocess, sys, os

def game_dir() -> Path:
    """Return the installation directory for the game."""
    # get user data directory (every os has a different path for it)
    base = Path(platformdirs.user_data_dir("rpg-battle"))
    # create game directory if it doesn't exist
    game = base / "game"
    game.mkdir(parents=True, exist_ok=True)
    # return game directory
    return game


def version_file() -> Path:
    """Return the version file path."""
    return game_dir() / "version.txt"


def installed_version() -> str | None:
    """Return the installed version of the game."""
    # get version file
    version = version_file()
    # if version file exists, return its content
    if version.exists():
        text = version.read_text().strip()
        return text if text else None
    return None


def save_version(version: str) -> None:
    """Save the version of the game."""
    # save version to file
    version_file().write_text(version)


def get_game_executable() -> Path:
    """Return the game executable."""
    base = game_dir()
    # find executable (in case of windows looking for "rpg_battle.exe", otherwise "rpg_battle")
    exe = base / ("rpg_battle.exe" if sys.platform == "win32" else "rpg_battle")
    return exe


def is_game_installed() -> bool:
    """Return True if the game is installed."""
    exe = get_game_executable()

    # fallback: check if game module exist (development environment)
    game_module = Path("game")
    return exe.exists() or (game_module.exists() and game_module.is_dir())


def launch_game() -> None:
    """Launch the game."""
    if not is_game_installed():
        raise RuntimeError("Game not found")

    base = game_dir()
    exe = get_game_executable()

    # try to run game if it exists
    if exe.exists():  # Production enviroment
        try:
            # run game (passing game directory as current working directory)
            subprocess.Popen([str(exe)], cwd=str(base), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))  # Windows-specific flag to prevent a console window from appearing
        except Exception as e:
            # if game doesn't exist, raise exception
            raise RuntimeError(f"Failed to launch game: {e}")
    else:  # Development enviroment
        try:
            # run game (passing game directory as current working directory)
            subprocess.Popen([sys.executable, "-m", "game.main"], cwd=str(base), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))  # Windows-specific flag to prevent a console window from appearing
        except Exception as e:
            # if game doesn't exist, raise exception
            raise RuntimeError(f"Failed to launch game: {e}")


def _asset_base() -> Path:
    """Base folder for bundled (in-memory) or development assets."""
    # in a frozen (PyInstaller) build, assets live in sys._MEIPASS
    if getattr(sys, "_MEIPASS", None):  # if MEIPASS exist, the launcher is compiled
        return Path(sys._MEIPASS) / "assets"
    # development: project root
    return Path(__file__).resolve().parent.parent / "game" / "assets"


def launcher_background_path() -> Path:
    """Return the path to the default carousel background."""
    # return path to default carousel background
    return _asset_base() / "backgrounds" / "rpg_battle_background_title.png"


def font_path(bold: bool) -> Path | None:
    """Return an existing font path for a heading (bold) or body (regular), or None."""
    # set a list of font paths to check for each OS
    candidates = [
        # Windows
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
        # macOS
        Path("/Library/Fonts") / ("Arial Bold.ttf" if bold else "Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental") / ("Arial Bold.ttf" if bold else "Arial.ttf"),
        # Linux
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    # return first valid font path, otherwise None
    for path in candidates:
        if path.exists():
            return path
    return None


def launcher_hero_path(index: int) -> Path:
    """Return the path to a hero sprite frame (1-8) for the download animation."""
    return _asset_base() / "sprites" / "hero" / f"hero_{index:02d}.png"
