from pathlib import Path

from PyInstaller.utils.hooks import collect_all


root = Path(SPECPATH)
datas = [(str(root / "frontend" / "dist"), "frontend/dist")]
binaries = []
hiddenimports = [
    "mlx_whisper",
    "mlx",
    "mlx.core",
    "silero_vad",
    "sounddevice",
]

for package in ("mlx_whisper", "mlx", "silero_vad"):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

analysis = Analysis(
    [str(root / "joshuasnotes" / "main.py")],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)
app_executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="JoshuaNotes",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)
collected = COLLECT(
    app_executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="JoshuaNotes",
)
bundle = BUNDLE(
    collected,
    name="Joshua Notes.app",
    icon=str(root / "assets" / "JoshuaNotes.icns"),
    bundle_identifier="com.joshuasnotes.joshuanotes",
    info_plist={
        "CFBundleDisplayName": "Joshua Notes",
        "CFBundleName": "Joshua Notes",
        "NSMicrophoneUsageDescription": "Joshua Notes records audio while you dictate notes.",
        "NSAppleEventsUsageDescription": "Joshua Notes pastes transcribed text into the active app.",
    },
)