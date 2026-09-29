#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python_bin=${PYTHON:-"$project_root/venv/bin/python"}

cd "$project_root"

if [ ! -x "$python_bin" ]; then
    echo "Python environment not found: $python_bin" >&2
    echo "Create the project venv and install the app dependencies first." >&2
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required to build the bundled frontend." >&2
    exit 1
fi

npm ci --prefix frontend
npm run build --prefix frontend
swift scripts/create_app_icon.swift assets
iconutil -c icns assets/JoshuaNotes.iconset -o assets/JoshuaNotes.icns
"$python_bin" -m pip install -r requirements-packaging.txt
"$python_bin" -m PyInstaller --noconfirm --clean --distpath dist --workpath build/pyinstaller WhisperFlow.spec

printf '\nBuilt app: %s\n' "$project_root/dist/Joshua Notes.app"