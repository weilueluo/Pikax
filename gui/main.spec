# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\University of Manchester\\Projects\\Pikax\\gui'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('assets/images/background.jpg', './assets/images/background.jpg', 'DATA')]
a.datas += [('assets/images/pikax_icon.ico', './assets/images/pikax_icon.ico', 'DATA')]
a.datas += [('cloudscraper/user_agent/browsers.json', './assets/browsers.json', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Pikax 0.2.3',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='assets/images/pikax_icon.ico')
