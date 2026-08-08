# RPG Battle — CS50x Final Project

Turn-based RPG battle game (Pygame) paired with a customTkinter launcher that
downloads the game from GitHub Releases and displays a news feed served from a
JSON file in this repository. Final project for CS50x 2026.

## Features

> Documented incrementally as each feature is implemented.

### Turn-based battle engine (Phase 1 — console logic)

Playable in the terminal with `python -m game.main`.

- Hero vs Enemy turn-based combat: physical attack, three mana-consuming
  rune skills (Spell, Guard, Heal) inspired by Suikoden II, potions, and a
  speed-based flee mechanic.
- Damage formula with defense reduction, a random range and 10% critical hits.
- Guard reduces the next incoming hit and is consumed on contact; battle logs
  report the actual damage dealt (after mitigation).
- Weighted enemy AI (attack / spell / guard) that falls back to attack when out
  of mana.
- Persistent score history stored in `game/scores.json` (ignored by git): each
  battle records date, result, turns, hero HP left/max and enemy name; a
  statistics view shows wins/losses/flees and the most common enemy.
- Main menu loop: play a battle, view statistics, or quit.

## Repository structure

- `game/` — the Pygame battle game.
- `launcher/` — the customTkinter downloader/runner.
- `news/` — the JSON news feed consumed by the launcher.
