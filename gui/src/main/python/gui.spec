# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import sysconfig
from pathlib import Path

is_windows = sys.platform.startswith("win")

project_root = Path.cwd()
dist_path = project_root / 'dist'

exe_name = "ytmusic-deleter.exe" if is_windows else "ytmusic-deleter"
exe_path = dist_path / exe_name

site_packages = sysconfig.get_paths()['purelib']

datas = []

if exe_path.exists():
    datas.append((str(exe_path), '_internal'))
else:
    print(f"WARNING: CLI executable not found at {exe_path}")

datas.append((
    os.path.join(site_packages, 'ytmusicapi', 'locales'),
    '_internal/ytmusicapi/locales'
))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name='YTMusic_Deleter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='YTMusic_Deleter',
)
