# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['NetGuardian\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('NetGuardian/config', 'config'), ('crdt-cluster/sync_folder', 'crdt_sync_folder'), ('crdt-cluster/config', 'crdt_config')],
    hiddenimports=['pkg_resources.py2_warn', 'paramiko.transport', 'paramiko.sftp_client', 'cryptography.hazmat.backends.openssl.backend', 'bcrypt', 'passlib.handlers.bcrypt', 'PIL._tkinter_finder'],
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
    name='NetGuardianMac',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
