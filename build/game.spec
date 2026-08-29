# build/game.spec
# PyInstaller spec for the RPG Battle game (onedir, windowed).

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("game")

a = Analysis(
    ["..\\game\\main.py"],
    pathex=["..\\"],
    binaries=[],
    datas=[
        ("..\\game\\assets\\backgrounds", "game\\assets\\backgrounds"),
        ("..\\game\\assets\\fonts",       "game\\assets\\fonts"),
        ("..\\game\\assets\\sfx",         "game\\assets\\sfx"),
        ("..\\game\\assets\\sprites\\hero",  "game\\assets\\sprites\\hero"),
        ("..\\game\\assets\\sprites\\enemy", "game\\assets\\sprites\\enemy"),
        ("..\\game\\assets\\sprites\\items", "game\\assets\\sprites\\items")
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
