# build/game.spec
# PyInstaller spec for the RPG Battle game (onedir, windowed).

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("game")

a = Analysis(
    [os.path.join("..", "game", "main.py")],
    pathex=[os.path.join("..", "game")],
    binaries=[],
    datas=[
        (os.path.join("..", "game", "assets", "backgrounds"), os.path.join("game", "assets", "backgrounds")),
        (os.path.join("..", "game", "assets", "fonts"),       os.path.join("game", "assets", "fonts")),
        (os.path.join("..", "game", "assets", "sfx"),         os.path.join("game", "assets", "sfx")),
        (os.path.join("..", "game", "assets", "sprites", "hero"),  os.path.join("game", "assets", "sprites", "hero")),
        (os.path.join("..", "game", "assets", "sprites", "enemy"), os.path.join("game", "assets", "sprites", "enemy")),
        (os.path.join("..", "game", "assets", "sprites", "items"), os.path.join("game", "assets", "sprites", "items"))
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
