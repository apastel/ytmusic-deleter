# -*- mode: python ; coding: utf-8 -*-

import os
import sysconfig

here = os.path.abspath(os.getcwd())

site_packages = sysconfig.get_paths()['purelib']

datas = [
    (
        os.path.join(site_packages, 'ytmusicapi', 'locales'),
        'ytmusicapi/locales'
    ),
    (
        os.path.join(here, 'gui', 'src', 'main', 'icons', 'Icon.ico'),
        'icons'
    )
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
    icon=os.path.join(here, 'gui', 'src', 'main', 'icons', 'Icon.ico'),
    console=False,
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
