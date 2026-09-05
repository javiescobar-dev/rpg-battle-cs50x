# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Handle news fetching and display."""

import urllib, time, json
from pathlib import Path
from paths import game_dir
from config import NEWS_URL, NEWS_CACHE_TTL, NEWS_BASE_URL


def fetch_news() -> list[dict]:
    """Fetch news from the remote URL."""
    # request news url
    req = urllib.request.Request(NEWS_URL)
    # open news url
    with urllib.request.urlopen(req) as resp:
        # load json
        data = json.loads(resp.read().decode())
    # return news items
    return data.get("items", [])


def cache_path() -> Path:
    """Get the cache path for news."""
    return game_dir().parent / "news_cache.json"


def save_cache(items: list[dict]) -> None:
    """Save news to cache."""
    cache_path().write_text(json.dumps({"items": items, "ts": time.time()}))


def load_cache() -> list[dict] | None:
    """Load news from cache with a time for expiration in case the network is not available."""
    # get cache path
    cp = cache_path()
    # if cache doesn't exist, return None
    if not cp.exists():
        return None
    # load cache
    data = json.loads(cp.read_text())
    # check if cache is expired
    if time.time() - data.get("ts", 0) > NEWS_CACHE_TTL:
        return None  # expired
    return data.get("items", [])


def get_news() -> list[dict]:
    """Get news, trying the network first and falling back to cache if needed."""
    try:
        # fetch news
        items = fetch_news()
        # save cache
        save_cache(items)
        # return news
        return items
    except Exception:
        # return cache
        return load_cache() or []


def image_cache_dir() -> Path:
    """Get the cache directory for news images."""
    directory = game_dir().parent / "news_images"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_image_path(image_field: str) -> Path | None:
    """Get the image path for the news item."""
    url = NEWS_BASE_URL + image_field
    dest = image_cache_dir() / Path(image_field).name
    # if the file already exists and is recent, do not download it
    if dest.exists() and time.time() - dest.stat().st_mtime <= NEWS_CACHE_TTL:
        return dest
    # try to download if it is old or doesn't exist
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            dest.write_bytes(resp.read())
        return dest
    except Exception:
        # If the network fails but you have an old copy, use it (better than nothing)
        return dest if dest.exists() else None
