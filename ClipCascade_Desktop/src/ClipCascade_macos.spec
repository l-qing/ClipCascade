# -*- mode: python ; coding: utf-8 -*-

import certifi
import importlib.util
import re
import subprocess

# PyInstaller rewrites dylib paths inside the bundle. A dynamically linked
# cryptography can then resolve to Python's different OpenSSL with the same
# filename, even when imports in the unfrozen environment succeed.
rust_binding = importlib.util.find_spec('cryptography.hazmat.bindings._rust')
if rust_binding is None or not rust_binding.origin:
    raise SystemExit('cryptography Rust binding is missing; install requirements_mac.txt')
linked_libraries = subprocess.check_output(
    ['otool', '-L', rust_binding.origin], text=True
)
if re.search(r'/lib(?:ssl|crypto)[^/\s]*\.dylib', linked_libraries):
    raise SystemExit(
        'cryptography links to a shared OpenSSL library, which can collide with '
        'the bundled Python OpenSSL. Reinstall official wheels in a fresh venv: '
        'python3 -m pip install --no-cache-dir -r requirements_mac.txt\n'
        + linked_libraries
    )

# Keep binaries and data inside the app bundle to avoid extraction on each launch
# and keep certifi's CA bundle available throughout long-running sessions.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[(certifi.where(), 'certifi')],
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['packaging/macos_self_test.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # binaries and data are collected by COLLECT below
    name='ClipCascade',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../../logo/logo.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClipCascade',
)
app = BUNDLE(
    coll,
    name='ClipCascade.app',
    icon='../../logo/logo.icns',
    bundle_identifier=None,
    info_plist={
        'LSUIElement': True,
    },
)
