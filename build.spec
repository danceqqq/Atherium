# build.spec
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

# Основной файл приложения
a = Analysis(
    ['main.py'],
    pathex=['.'],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebChannel',
        'requests',
        'json',
        'random',
        'os',
        'sys'
    ],
    datas=[
        ('static', 'static'),  # HTML/CSS/JS
        ('music', 'music'),    # Музыкальные файлы
        ('img', 'img'),        # Изображения
        ('.cache', '.cache')   # Кэш-директория
    ],
    binaries=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GameLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Скрыть консоль
    icon='icon.ico'  # Ваша иконка (если есть)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GameLauncher'
)