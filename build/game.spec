# build/game.spec
# PyInstaller spec for the RPG Battle game (onedir, windowed).

import os
from PyInstaller.utils.hooks import collect_submodules

game_dir = os.path.abspath(os.path.join(SPECPATH, "..", "game"))

hiddenimports = collect_submodules("game")

a = Analysis(
    [os.path.join(game_dir, "main.py")],
    pathex=[game_dir],
    binaries=[],
    datas=[
        (os.path.join(game_dir, "assets", "backgrounds"), os.path.join("game", "assets", "backgrounds")),
        (os.path.join(game_dir, "assets", "fonts"),       os.path.join("game", "assets", "fonts")),
        (os.path.join(game_dir, "assets", "sfx"),         os.path.join("game", "assets", "sfx")),
        (os.path.join(game_dir, "assets", "sprites", "hero"),  os.path.join("game", "assets", "sprites", "hero")),
        (os.path.join(game_dir, "assets", "sprites", "enemy"), os.path.join("game", "assets", "sprites", "enemy")),
        (os.path.join(game_dir, "assets", "sprites", "items"), os.path.join("game", "assets", "sprites", "items"))
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "PIL", "customtkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="rpg_battle",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="game",
)
