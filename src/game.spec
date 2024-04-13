# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

a.datas += [('enemy0.png', './asset/enemy0.png', 'DATA'),
            ('enemy1.png', './asset/enemy1.png', 'DATA'),
            ('bread_boy.png', './asset/bread_boy.png', 'DATA'),
            ('dead.png', './asset/img/dead.png', 'DATA'),
            ('stage0.csv', './asset/stage0.csv', 'DATA'),
            ('stage1.csv', './asset/stage1.csv', 'DATA'),
            ('bgm.mp3', './asset/bgm.mp3', 'DATA'),
            ('se_8bit26.mp3', './asset/se_8bit26.mp3', 'DATA'),
            ('se_battle06.mp3', './asset/se_battle06.mp3', 'DATA'),
            ('se_battle14.mp3', './asset/se_battle14.mp3', 'DATA'),
            ]

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='game',
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
