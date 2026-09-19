# RPG Battle - CS50x Final Project

#### Video Demo: <demo video URL (pending recording)>

#### Repository: <https://github.com/javiescobar-dev/rpg-battle-cs50x>

#### Description

RPG Battle is a turn-based combat game in the style of Suikoden II built with
Python and Pygame, accompanied by a desktop launcher in customTkinter that
downloads, updates and launches the game from GitHub *releases*. The idea comes
from emulating CS50x's first exercise, the Week 0 project in Scratch, which was
precisely an RPG battle, and to complement it I decided to include a launcher
that eases distribution, keeps it updated and shows news and new versions. The
project is also a way to practice designing a complete Python program: game
logic decoupled from the graphics, a state machine, event-driven animations,
data persistence and a distribution pipeline (PyInstaller builds and CI with
GitHub Actions).

Opening the game shows a main menu with the options Play, Statistics and Quit.
Every battle is turn-based: the hero chooses to attack, use a skill (Fireball,
Guard or Heal), take a potion or flee, and the enemy acts with a weighted AI.
Each combat randomly picks a hero, an enemy and a scene, and its result is saved
to a JSON file (`scores.json`) that is later loaded in the end-of-battle and
statistics screens. The launcher shows the project news in an image carousel,
and lets you install, update or uninstall the game with one click.

## The game

**The combat.** Each turn the hero chooses between attacking physically,
casting one of the three maná-consuming skills (Fireball, Guard and Heal),
taking a potion to recover health or trying to flee; fleeing is resolved
according to relative speed. The enemy decides its action with a weighted AI
between attack, spell and guard, falling back to attack when it runs out of
maná. Damage is computed with a formula that reduces the target's defense,
applies a random range and has a 10% chance of a critical hit; guard reduces
the next incoming action and is consumed on contact, and the combat log reports
the actual, already-mitigated damage.

**The battle scene.** The combat is presented on a field with depth in the
Suikoden II style: the enemy sits at the top left with a slightly smaller scale
(0.95, a bit farther away) and the hero at the bottom right closer to the
camera (1.1), with a dynamic scale change that sells the depth during the
movements. The hero's fixed card (portrait, name and HP/MP bars) occupies the
top-right corner; the enemy's values stay hidden to keep the tension, showing
only its name above it. A log panel with the latest combat lines scrolls
through the events with line wrapping.

**Navigation.** The main menu (Play, Statistics, Quit) and the two-level battle
menu (Attack / Skill / Potion / Flee, with the Fireball / Guard / Heal / Back
skill submenu) share a single cursor: it moves with the keyboard (arrows +
Enter, with number shortcuts) or with the mouse (hover moves it and click
confirms).

**Animations.** The engine does not draw anything: it generates events that an
`EventPlayer` plays back one by one. The physical attack is a diagonal lunge
that stops before the target, with an impact flash, a defender knockback and
the damage number rising and fading; on the way back, the attacker jumps
backwards while keeping its eyes on the target and its scale changes to
reinforce the depth. Spells fire a bright projectile with a trail, a pulse and
explosion rings on impact (orange for the hero, purple for the enemy). Healing
raises a tornado of green particles that wraps around the character, guard
draws an arc shield with three layers tilted diagonally toward the opponent and
the potion makes the animated sprite of a bottle float over the head. Numbers
and messages are colored by type: yellow for damage, red and big with "!" for
criticals, green for heals and potions, light blue for guard and whitish for
misses. The combat log advances live, one line per event, and the game only
returns to the menu or ends when the last animation is finished.

**Resources.** The characters use pixel-art sprite sheets (Pixel Champions II)
of 864×576 pixels. On load, every sheet is cut into 96×96 cells and stored in a
per-pose dictionary with 3 frames each (18 poses, plus a `run` pose derived from
`flee` by flipping it horizontally); launching an action plays the stored
animation for that pose. There are 8 heroes and 5 enemies, and every battle also
picks one of 4 pixel-art backgrounds at random (castle, forest, cave, harbor).
Several WAV sound effects are associated with the actions and sound at the
specific phases (lunge, launch, impact), with cursor blips in the menus; they
were obtained with a license from itch.io (Leohpaz), just like the sprite
sheets (Pixel Champions II). The title and end screens use backgrounds with a
dark overlay for contrast with the text and a fade-to-black transition between
screens; the end title is painted at 64 px with a color that reflects the
outcome (gold on victory, red on defeat), and the statistics are shown in an
aligned table with accent-colored values inside a semi-transparent panel whose
layout is defined in `config.py`.

## The launcher

**Role.** It is the user's entry point: it downloads, updates, launches and
uninstalls the game directly from the GitHub *Releases* and shows the project
news in a carousel.

**Window.** It is a window without a native frame (the title bar is hidden with
a *hidden titlebar* technique that keeps the native Windows shadow and
animations), organized in three horizontal bands: a header with the title
rendered with the same font as the game and its underline bar, a central area
with the carousel and a footer with the installed version, the buttons (Play,
Download/Update, Uninstall) and the progress bar. Minimize and close are custom
buttons with Flaticon icons (close, minimize and theme toggle), and the header
is draggable. The executable icon is shared by the game and the launcher and was
generated with AI.

**Themes.** It has a light and a dark theme, switchable from the sun/moon icon
button on the top-left corner. The light theme uses a white background with
cyan accents and the dark one a charcoal background with golden accents; both
outline the main window and the carousel with black borders for a stylish touch.
The change is a hot recolor of the widgets, without rebuilding the interface or
flashing, and the selected theme is saved to a JSON file (`settings.json`), so
that opening the launcher keeps the last chosen theme.

**News carousel.** It loads `news.json` from GitHub (both the description and
the image paths) with a one-hour local cache (and the last known copy if
offline). For each news item it reads its title, body and image path, and
draws everything together (image cropped without distortion to fill the frame,
overlay, text, arrows and navigation dots) into a single composite image. The
interaction is therefore a click handler over that image: depending on the zone
you press, one action or another runs, like going to the previous or next news
item with the arrows or jumping to the item of a specific dot. This design was
chosen because customTkinter cannot overlay widgets with transparency on top of
images; everything is solved by painting. The slide change is animated with a
sliding transition.

**Download and versioning.** On startup it queries the latest GitHub release
and compares it with the locally installed version to configure the button:
"Download" if nothing is installed, "Update" if a newer version exists and "Up
to date" (disabled) if it is already current. From the release it picks the zip
of the operating system it runs on (`rpg-battle-<platform>-<version>.zip`),
downloads it to a temporary folder and extracts it into the user data directory
that corresponds to that operating system. During the download it shows a
progress bar with a hero sprite running on it, using the same animation and
technique as the game (specifically the Flee pose, running toward the right in
the same direction the bar advances), with a random hero in each download;
while it downloads or uninstalls, the footer buttons are disabled and when it
finishes they are enabled again according to the result (Play and Uninstall when
there is a game installed, and the download button is updated). When done it
saves the installed version and enables Play. "Uninstall" cleans the game, the
versions, the caches, the log and the settings in a single action, with a
confirmation first.

**Reliability.** Every network operation logs in `launcher.log` the exact phase
that fails (release query, asset lookup, download, extraction) with a 20-second
timeout. TLS verification uses `truststore` to validate against the system
certificate store, which avoids the typical failures in corporate networks or
virtual machines where antivirus software intercepts HTTPS; this verification
was added precisely because, while testing the launcher in a Windows 11 virtual
machine, the validation of the system certificates failed. Data paths use
`platformdirs` (the user data directory of each operating system), never the
executable's folder.

## File structure

The game source code lives in `game/`:

- `game/config.py` - all the constants and the game balance: screen size,
  colors, fonts, HP/MP values, damages, hero/enemy/background lists, asset
  paths and screen layout.
- `game/entities.py` - the `Entity` class (name, stats, HP/MP, defense, etc.),
  the `Hero` and `Enemy` characters, and the enemy AI decision logic.
- `game/battle.py` - the turn-based combat engine, pure Python without Pygame:
  the damage formula (defense, random range and critical), the actions
  (attack, spell, guard, potion, flee) and the generation of events that feed
  the log.
- `game/score.py` - results history: saves every battle to `scores.json`
  (date, outcome, turns) and computes the statistics summary.
- `game/ui.py` - the whole visual side of the game: character sprites, battle
  panels, the log, the menus and the event-driven animations (attack, spells,
  heal, guard and potion).
- `game/assets.py` - resource loading: sprite sheets, backgrounds, sound
  effects, fonts and the icon.
- `game/main.py` - the main loop and the state machine (MENU / STATS / BATTLE /
  ANIM / END), together with the drawing of each screen.

The launcher lives in `launcher/`:

- `launcher/config.py` - application constants (name, canonical URLs for
  releases and news).
- `launcher/paths.py` - cross-platform data paths, version management, the
  installation check and the game startup.
- `launcher/updater.py` - queries the latest GitHub *release*, downloads the
  platform zip with a progress bar and installs it.
- `launcher/news.py` - fetches, caches and processes the `news.json` news feed.
- `launcher/ui_styles.py` - color palettes of the light and dark themes.
- `launcher/settings.py` - local settings persistence (`settings.json`).
- `launcher/diag.py` - diagnostic logging and TLS verification with
  `truststore`.
- `launcher/main.py` - the main window (background, carousel, themes, buttons).

Other files:

- `build/game.spec` and `build/launcher.spec` - PyInstaller configurations to
  package both programs.
- `.github/workflows/build.yml` - CI that builds the game and the launcher on
  Windows, macOS and Linux and publishes a GitHub *release* per tag.
- `news/news.json` - the news feed consumed by the launcher.

## Design decisions

- **Engine separated from the interface.** `battle.py` does not import Pygame:
  the combat logic can be run and tested in the console (in fact Phase 1 was
  playable in the terminal). This keeps the mechanics clean and independent of
  the presentation.
- **Events instead of coupling the simulation to the animation.** The engine
  does not animate anything: it generates a list of events (attack, damage,
  heal, flee…) that an `EventPlayer` plays back one by one as animations. The
  battle only advances when the current animation finishes, which controls the
  pacing and avoids inconsistent states.
- **Animations based on simple physics.** Trails, projectiles and particles are
  computed with vectors and per-frame phasing instead of predefined sprites,
  which allows smooth effects (trail, bounce, healing swirl) without relying on
  giant animation sheets.
- **Pygame-ce instead of Pygame.** The *community edition* was chosen, the
  maintained fork that is up to date and works well with modern Python.
- **customTkinter for the launcher.** `tkinter` allows a lightweight program
  without heavy dependencies; `customtkinter` brings light/dark themes and
  modern widgets. Switching theme is a simple hot color change, which avoids
  rebuilding the interface and flashing.
- **Distribution through *Releases*.** The launcher knows no private servers:
  it consumes the public GitHub API (`latest release`) to download the correct
  binary. The whole cycle is safe and automated: it is built in GitHub Actions,
  the `release` branch is protected (only the owner can publish), a `v*` tag
  triggers the build and the release is born as a *Draft* to review before
  publishing it.
- **Silent failures that are not.** Every network path writes a log with the
  exact phase that fails and timeouts are capped; the news and image caches
  survive disconnection. This way the launcher works offline and problems are
  diagnosed without guessing.
- **Persistence in the user data directory.** Games and caches are saved with
  `platformdirs` to the path each operating system corresponds to, instead of
  next to the executable (which may be read-only).
- **`--onedir` packaging with CI.** `PyInstaller` in folder mode reduces
  antivirus false positives and starts faster; GitHub Actions builds the three
  platforms and publishes the releases, and asset paths resolve with
  `sys._MEIPASS`, so the executable works from any folder.
- **Real pixel-art sprites.** Instead of geometric shapes, the characters use
  sprite sheets (Pixel Champions II) scaled with `smoothscale` and a dynamic
  factor for the depth effect. The result looks far more attractive than the
  placeholders without complicating the asset loading too much.
- **The launcher as a separate application.** The game is packaged as a
  portable zip the launcher downloads; the launcher is the only piece the user
  opens and it takes care of installing, updating and launching the game.
  Separating the two applications allows distributing game updates without
  recompiling the launcher and keeps each binary small.
- **Resource attribution.** The sprites come from Pixel Champions II and the
  sound effects from Leohpaz, both from itch.io with a license; the header
  icons (close, minimize, theme) are from Flaticon; the executable icon and the
  pixel-art backgrounds were generated with the help of AI. The use of the AI
  tool that accompanied the development is cited in the header of every source
  file, as the course policy requires.

## Running and building

In development:

```bash
python -m game.main
```

The launcher only needs to run in Python mode if a `game/` folder exists (it
uses `python -m game.main` automatically); in production it is built with
PyInstaller from `build/game.spec` and `build/launcher.spec`.

The game and the launcher are designed to build and run cross-platform
(Windows, Linux and macOS). GitHub Actions builds, per operating system, one
game executable and one launcher executable, 6 executables in total, and each
one is compressed into a separate zip for distribution. The process is as
follows: first I move the changes from the `dev` branch to the `release` branch
through a safe pull request; then I push a `v*` tag with the new version, which
triggers the workflow. When it finishes building and compressing, it generates
a new *Draft* release, which I review manually and publish safely.

## Note

The English README submitted to CS50x was written with the help of an AI
assistant for the translation, since English is not my native language and it
is not yet at the level I would like; the AI usage notice is also cited in the
header of every source file, as the course policy requires.