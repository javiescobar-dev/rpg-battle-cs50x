# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Handle news fetching and display."""

import urllib, time, json
from pathlib import Path
from paths import game_dir
from config import NEWS_URL, NEWS_CACHE_TTL


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
