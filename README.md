# RPG Battle — CS50x Final Project

Turn-based RPG battle game (Pygame) paired with a customTkinter launcher that
downloads the game from GitHub Releases and displays a news feed served from a
JSON file in this repository. Final project for CS50x 2026.

## Features

> Documented incrementally as each feature is implemented.

### Turn-based battle engine (Phase 1, console logic)

- Hero vs Enemy turn-based combat: physical attack, three mana-consuming
  rune skills (Spell, Guard, Heal) inspired by Suikoden II, potions, and a
  speed-based flee mechanic.
- Damage formula with defense reduction, a random range and 10% critical hits.
- Guard reduces the next incoming hit and is consumed on contact; battle logs
  report the actual damage dealt (after mitigation).
- Weighted enemy AI (attack / spell / guard) that falls back to attack when out
  of mana.
- Tested in the console (`python -m game.main` once Phase 1 is complete).

*Pending within Phase 1: score recording (`score.py`) and the console menu
loop (`main.py`).*

## Repository structure

- `game/` — the Pygame battle game.
- `launcher/` — the customTkinter downloader/runner.
- `news/` — the JSON news feed consumed by the launcher.
