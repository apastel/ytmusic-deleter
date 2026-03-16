# -*- mode: python ; coding: utf-8 -*-

import os
import site
import sys
import sysconfig
from pathlib import Path

# Get paths
project_root = (Path.cwd() / sys.argv[0]).parent.parent.parent.parent.parent
venv_path = project_root / '.venv'
dist_path = project_root / 'dist'
exe_path = dist_path / 'ytmusic-deleter.exe'

# Get site-packages
site_packages = sysconfig.get_paths()['purelib']

# Data files to include
datas = [
    (str(exe_path), '_internal'),  # CLI executable
    (os.path.join(site_packages, 'ytmusicapi', 'locales'), '_internal/ytmusicapi/locales'),  # ytmusicapi locales
]

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
