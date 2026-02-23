# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('llama_cpp')
binaries += collect_dynamic_libs('opencv-python')


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=[('main.kv', '.'), ('mic_white.png', '.'), ('mic_green.png', '.')],
    hiddenimports=['cv2', 'kivy', 'kivy.core.window', 'kivy.graphics', 'kivy.uix.camera'],
    hookspath=['.'],
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
    name='MyApp',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyApp',
)
