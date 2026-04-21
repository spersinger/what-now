# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('llama_cpp')
binaries += collect_dynamic_libs('opencv-python')


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('ui/whatnow.kv', 'ui'),
        ('ui/themed.kv', 'ui'),
        ('ui/home_page.kv', 'ui'),
        ('ui/voice_page.kv', 'ui'),
        ('ui/scanner_page.kv', 'ui'),
        ('mic_white.png', '.'),
        ('mic_green.png', '.'),
        ('models/*', 'models'),
    ],
    hiddenimports=['cv2', 'kivy', 'kivy.core.window', 'kivy.graphics', 'kivy.uix.camera', 'desktop_notifier.resources'],
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
    name='WhatNow',
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
    name='WhatNow',
)
