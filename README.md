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

### Pygame UI (Phase 2 — in progress)

Launched with `python -m game.main`. A Suikoden II-style battle screen on top of
the Phase 1 engine (unchanged battle logic).

- 960x640 window at 60 FPS with structured battle events: the engine log now
  stores dicts (attack / spell / guard / heal / potion / mana/potion failures /
  flee / defeated) and a `format_event()` renders the same messages as Phase 1,
  keeping the visual log and the semantics identical.
- Suikoden II-style field with depth: the enemy stands up-left and smaller
  (0.8 scale, further away) while the hero stands down-right at full scale
  (closer). The hero's status is shown in a fixed framed card at the top-right
  (name + HP/MP bars); the enemy's HP/MP stay hidden for combat tension, with
  only a name plate above the enemy. A scrolling combat log panel shows the
  last six `format_event` messages with word wrapping.
- Main menu (Play / Statistics / Quit) with a single cursor shared by keyboard
  (arrow keys + Enter, number shortcuts 1-3) and mouse (hover moves the cursor,
  click confirms).
- Suikoden II-style two-level battle menu: Attack / Skill / Potion / Flee, where
  choosing Skill swaps the panel for the rune submenu Fireball / Guard / Heal / Back.
  Same navigation as the main menu (arrows + Enter, keys 1-4, mouse).
- The game flow is driven by a state machine (menu / battle / animation / end /
  stats): Play starts a battle, choosing an action resolves the turn instantly and
  the new events appear in the log, and a finished battle is recorded to the score
  history. The end screen shows the result with a flavor line (e.g. "Hero vs Enemy -
  5 turns") plus the global summary, and a statistics screen shows the same summary
  from the main menu; both return to the menu on any key or click. Animations
  (lunge / flash / recoil / floating damage numbers) are the next step.

## Repository structure

- `game/` — the Pygame battle game.
- `launcher/` — the customTkinter downloader/runner.
- `news/` — the JSON news feed consumed by the launcher.
