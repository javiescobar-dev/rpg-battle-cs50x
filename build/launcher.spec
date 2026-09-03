# build/launcher.spec
# PyInstaller spec for the RPG Battle launcher (onedir, windowed).

import os

launcher_dir = os.path.abspath(os.path.join(SPECPATH, "..", "launcher"))

hiddenimports = []  # main.py imports its modules by bare name (from config import ...);
                    # they are resolved through pathex below, not collected as launcher.*

a = Analysis(
    [os.path.join(launcher_dir, "main.py")],            # entry point
    pathex=[launcher_dir],                              # paths of bare imports (config, paths, ...)
    binaries=[],
    datas=[
        (os.path.join(launcher_dir, "..", "game", "assets", "backgrounds", "rpg_battle_background_title.png"),
        os.path.join("assets", "backgrounds")),
        (os.path.join(launcher_dir, "..", "game", "assets", "sprites", "hero", "*.png"),
        os.path.join("assets", "sprites", "hero"))
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["pygame", "pygame-ce"],   # launcher does not use Pygame
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="rpg_battle_launcher",
    debug=False,
    strip=False,
    upx=True,
    console=False,                      # --windowed
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="launcher",                    # dist/launcher/
)
