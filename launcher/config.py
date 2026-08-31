# RPG Battle - CS50x Final Project
# Developed with the assistance of an AI coding assistant (opencode).

"""Launcher configuration."""

# Game info
APP_NAME = "RPG Battle"

# GitHub API
REPO_API_URL = "https://api.github.com/repos/javiescobar-dev/rpg-battle-cs50x/releases/latest"

# News
NEWS_URL = "https://raw.githubusercontent.com/javiescobar-dev/rpg-battle-cs50x/main/news/news.json"

# Game asset pattern (must match the CI zip name: platform first, then tag)
GAME_ASSET_PATTERN = "rpg-battle-{platform}-{tag}.zip"

# Cache
NEWS_CACHE_TTL = 3600  # 1 hour in seconds
