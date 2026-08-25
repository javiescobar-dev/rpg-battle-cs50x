# RPG Battle — CS50x Final Project

Turn-based RPG battle game built with Pygame, paired with a customTkinter
launcher that downloads the game from GitHub Releases and displays a news
feed. Features Suikoden II-style combat animations, real sprite graphics,
and a polished battle UI. Final project for CS50x 2026.

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

### Pygame UI (Phase 2)

Launched with `python -m game.main`. A Suikoden II-style battle screen on top of
the Phase 1 engine (unchanged battle logic).

- 960x640 window at 60 FPS with structured battle events: the engine log now
  stores dicts (attack / spell / guard / heal / potion / mana/potion failures /
  flee / defeated) and a `format_event()` renders the same messages as Phase 1,
  keeping the visual log and the semantics identical.
- Suikoden II-style field with depth, centered on the screen: the enemy stands
  upper-left and slightly further away (0.95 scale) while the hero stands
  lower-right, closer to the camera (1.1 scale); the enemy is tuned to read
  slightly larger than the hero when their distances to the camera equalize.
  The hero's status is shown in a fixed framed card at the top-right (name +
  HP/MP bars); the enemy's HP/MP stay hidden for combat tension, with only a
  name plate above the enemy. A scrolling combat log panel shows the last six
  `format_event` messages with word wrapping.
- Main menu (Play / Statistics / Quit) with a single cursor shared by keyboard
  (arrow keys + Enter, number shortcuts 1-3) and mouse (hover moves the cursor,
  click confirms). A copyright footer is displayed at the bottom of the screen.
- Suikoden II-style two-level battle menu: Attack / Skill / Potion / Flee, where
  choosing Skill swaps the panel for the rune submenu Fireball / Guard / Heal / Back.
  Same navigation as the main menu (arrows + Enter, keys 1-4, mouse).
- The game flow is driven by a state machine (menu / battle / animation / end /
  stats): Play starts a battle, choosing an action resolves the turn instantly and
  the new engine events are queued to an EventPlayer, and a finished battle is
  recorded to the score history. The end screen shows the result with a flavor line
  (e.g. "Hero vs Enemy - 5 turns") plus the global summary, and a statistics screen
  shows the same summary from the main menu; both return to the menu on any key or
  click.
- Battle animations driven by the EventPlayer: events play one at a time as
  animations. AttackAnimation plays a diagonal lunge toward the target (stopping
  30px short), an impact flash (drawn on a translucent SRCALPHA overlay), a recoil
  (the defender is knocked back along the line of the blow) and a rising, fading
  damage number; on the way back the attacker hops in an arc — a backward leap
  that keeps its eyes on the target — while its apparent scale shifts to sell the
  depth (the hero shrinks as it moves away from the camera, the enemy grows as it
  comes closer). SpellAnimation is a ranged variant: a glowing projectile flies
  from the caster to the target, then a flash and the damage number appear on
  impact (the caster stays still, no lunge or recoil). Projectile color is
  orange for hero spells and purple for enemy spells. Heal, potion, guard, flee
  and failure events show a short floating message. Numbers are colored by type: yellow for damage, red and larger
  with a "!" for critical hits, green +N for heal/potion, light blue for guard and
  whitish for failures. The combat log streams live, one line per event, as each
  animation starts, and the game only returns to the battle menu or ends after the
  last animation finishes.
- Polished combat feel: floating numbers and messages are pre-rendered with a
  black outline and stay fully opaque until halfway through their rise, then fade
  out. The hero's HP/MP card updates progressively rather than all at once: every
  event carries an HP/MP snapshot, the mana cost is shown as the skill starts
  (including guard and heal), the defender's HP drops exactly at the moment of
  impact, and heals/potions raise HP as their animation plays.

### Polished graphics (Phase 3)

Sprites and asset pipeline replacing the Phase 2 placeholders.

- Pixel Champions II sprite sheets (864x576 px, 96x96 px frames) loaded via
  `assets.py`: each character PNG is split into 18 animation poses of 3 frames
  (idle, lunge, defend, use_magic, potion, hit, defeated, flee, victory, and
  more). A 19th pose, `run`, is derived from `flee` flipped horizontally.
- `CharacterSprite` draws the current animation frame with
  `pygame.transform.smoothscale`, applying a base scale (1.1 hero, 0.95 enemy)
  and a dynamic `scale_factor` for depth during lunges, all centered on the
  character's world position with offset support for movement animations. A
  `flip_x` flag mirrors the sprite so the enemy faces the hero.
- `set_idle_pose()` checks the character's HP on every animation reset: below
  20% the sprite shows the `caution` pose instead of `idle`.
- Sprite poses are driven per phase inside `AttackAnimation` and
  `SpellAnimation`: the attacker runs (`run`), strikes (`lunge`), then returns
  to idle/caution; the defender briefly shows `hit` on impact. Each transition
  fires once via dedicated flags (`_pose_lunge_done`, `_pose_recover_done`,
  `_pose_recoil_done`).
- Sprite loading is integrated into the battle startup: `start_battle()` loads
  hero and enemy sprite sheets once and passes them to the sprite constructors;
  the main loop advances sprite frame timers during the animation state.
- Battle backgrounds: four AI-generated pixel art scenes (castle, forest, cave,
  port) in Suikoden II style, loaded via `load_background()` and drawn before
  sprites.
- Random asset selection each battle: 8 heroes, 5 enemies, and 4 backgrounds
  are defined as tuple lists `(path, name)` in `config.py`; `start_battle()`
  picks one of each via `random.choice()`.
- Sound effects: 14 WAV files mapped by action in a `SFX` dict, loaded with
  caching via `load_sound()`. Battle sounds trigger at event start or at
  specific animation phases (lunge, cast, impact). Menu navigation plays
  cursor blips on option change and a confirm sound on selection, with a
  short delay before executing the chosen battle action.
- Title and end screens display background images with a dark semi-transparent
  overlay for text readability. A fade-through-black transition plays when
  starting a battle or viewing results. The end screen title is rendered at
  64 px with a color that matches the battle outcome (gold for victory, red
  for defeat). Battle statistics are shown as a left-aligned table with
  labels and accent-colored values inside a semi-transparent panel.
- Menus and the combat log use semi-transparent dark backgrounds with a
  black border. The hero status card shows a cropped portrait from the
  character's idle sprite alongside name and HP/MP bars. Battle input is
  locked during the action delay to prevent duplicate confirmations.
  Clicking outside a menu no longer triggers a confirm sound.
- Spell projectiles (Fireball and Shadow Bolt) feature a trailing
  afterimage, a pulsating glow, decorative particles that fly backward
  during travel, and an impact explosion with two expanding color-shifting
  rings. Each spell uses a three-color particle palette (yellow-orange-red
  for Fireball, purple-green for Shadow Bolt) with continuous emission
  during flight and a radial burst on impact. The projectile core glows
  in a brighter, differentiated color through a three-layer radial gradient.

## Repository structure

- `game/` — the Pygame battle game (`python -m game.main`).
- `game/assets/` — sprites, backgrounds, sound effects, and fonts.
- `launcher/` — the customTkinter downloader/runner.
- `news/` — the JSON news feed consumed by the launcher.
