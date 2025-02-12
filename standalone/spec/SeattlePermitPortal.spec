# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

def get_pandas_path():
  import pandas
  pandas_path = pandas.__path__[0]
  return pandas_path

a = Analysis(['SeattlePermitPortal.py'],
             pathex=['C:\\Users\\austi\\Dropbox (ACH)\\Intern Projects\\Seattle Permit Scheduler'],
             binaries=[('C:\\Users\\austi\\Dropbox (ACH)\\Intern Projects\\Seattle Permit Scheduler\\chromedriver.exe', 'selenium\\webdriver')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SeattlePermitPortal',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )