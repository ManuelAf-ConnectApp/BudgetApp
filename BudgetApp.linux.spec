# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ICON_FILE = Path("assets/app_icon.png")
MANUAL_FILE = Path("docs/Budget_App_Manual_es.pdf")

# The Spanish manual is bundled only when present in the repo; the app does not
# require it at runtime, so a missing PDF must not break the build.
datas = [
    ("assets/app_icon.png", "assets"),
    ("assets/connectapp_logo.jpg", "assets"),
]
if MANUAL_FILE.exists():
    datas.append((str(MANUAL_FILE), "docs"))


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "mysql.connector.locales",
        "mysql.connector.locales.eng",
        "mysql.connector.plugins",
        "mysql.connector.plugins.mysql_native_password",
        "mysql.connector.plugins.caching_sha2_password",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BudgetApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_FILE) if ICON_FILE.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BudgetApp",
)
