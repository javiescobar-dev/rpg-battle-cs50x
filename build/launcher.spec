# build/launcher.spec
# PyInstaller spec for the RPG Battle launcher (onedir, windowed).

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("launcher")

a = Analysis(
    ["..\\launcher\\main.py"],          # entry point
    pathex=["..\\launcher"],            # paths of bare imports (config, paths, ...)
    binaries=[],
    datas=[],                            # launcher does not package local assets
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
