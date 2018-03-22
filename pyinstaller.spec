# -*- mode: python -*-

block_cipher = None


a = Analysis(['fulltext\\__main__.py'],
             binaries=None,
             datas=[
                ('fulltext/*', 'fulltext/'),
                ('fulltext/backends/*', 'fulltext/backends'),
                ('fulltext/data/bin32', 'fulltext/data/bin32'),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='fulltext',
          debug=False,
          strip=False,
          upx=False,
          console=True )
