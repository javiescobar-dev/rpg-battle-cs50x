# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Manage game updates."""

import json, platform, urllib.request, zipfile, shutil, tempfile
from pathlib import Path
from config import REPO_API_URL, GAME_ASSET_PATTERN
from paths import game_dir, save_version


def platform_tag() -> str:
    """Return the platform tag for the current platform."""
    system = platform.system()
    # set tag
    tags = {"Windows": "windows", "Darwin": "macos", "Linux": "linux"}
    return tags.get(system, system.lower())


def fetch_latest_release() -> dict:
    """Fetch the latest release information from the GitHub API."""
    req = urllib.request.Request(REPO_API_URL)
    # get release info from github api
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def find_asset(release: dict, tag: str) -> dict | None:
    """Find the asset for the current platform and tag."""
    # set asset name pattern for current platform and tag
    expected = GAME_ASSET_PATTERN.format(tag=tag, platform=platform_tag())
    # find asset in release
    for asset in release.get("assets", []):
        if asset["name"] == expected:
            return asset
    return None


def download_asset(asset: dict, dest_dir: Path, progress_callback=None) -> Path:
    """Download the asset to the given path."""
    # get asset url
    url = asset["browser_download_url"]
    # get asset name
    dest = dest_dir / asset["name"]

    # request asset url
    req = urllib.request.Request(url)
    # get total size
    with urllib.request.urlopen(req) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        # open destination file
        with open(dest, "wb") as f:
            # read asset in chunks
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                # update progress bar (callback for UI)
                if progress_callback and total:
                    progress_callback(downloaded / total)  # 0.0 to 1.0
    
    return dest


def update(tag: str, progress_callback=None) -> bool:
    """Update the game to the given tag."""
    try:
        # get release info from github api
        release = fetch_latest_release()
        # find asset for current platform and tag
        asset = find_asset(release, tag)
        if not asset:
            return False

        # set destination directory (game directory)
        dest = game_dir()
        # download the asset to a temporary directory (keeps the zip out of game_dir)
        with tempfile.TemporaryDirectory() as tmp_dl:
            zip_path = download_asset(asset, Path(tmp_dl), progress_callback)

            # extract zip (overwrite existing game), flattening the outer "game/" folder
            with tempfile.TemporaryDirectory() as tmp:
                # extract zip to a temporary directory
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(tmp)
                # get the source directory (game directory)
                src = Path(tmp) / "game"
                src = src if src.is_dir() else Path(tmp)
                # delete the entire destination for a clean re-extraction
                if dest.exists():
                    shutil.rmtree(dest)
                # create the destination directory
                dest.mkdir(parents=True, exist_ok=True)
                # copy the source directory to the destination directory
                shutil.copytree(src, dest, dirs_exist_ok=True)

        # save new version
        save_version(tag)
        return True   # update success
    except Exception:
        return False  # update failed
