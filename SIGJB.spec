# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SIGJB.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\ti_tr\\\\Downloads\\\\Inventário_Out\\\\secret.key', '.'), ('C:\\\\Users\\\\ti_tr\\\\Downloads\\\\Inventário_Out\\\\.env.enc', '.')],
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
    a.binaries,
    a.datas,
    [],
    name='SIGJB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['img\\jb_icon_64x64.ico'],
)
