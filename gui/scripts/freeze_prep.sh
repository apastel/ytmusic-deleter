#!/bin/bash
set -e

echo Set up directories
VENV_PATH=$PDM_PROJECT_ROOT/.venv
if [[ $(uname) == "Linux" ]]; then
    VENV_BIN="bin"
    SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
else
    VENV_BIN="Scripts"
    SITE_PACKAGES=$VENV_PATH/Lib/site-packages
fi
EXE_PATH=$VENV_PATH/$VENV_BIN/ytmusic-deleter
FREEZE_DIR=$PDM_PROJECT_ROOT/gui/src/freeze

echo Activate the venv
source "$VENV_PATH/$VENV_BIN/activate"

echo Build the CLI executable in non-editable mode
pdm install --no-editable

echo Clean and re-create the freeze directories
rm -rf "$FREEZE_DIR"
mkdir -p "$FREEZE_DIR"/linux/_internal/ytmusicapi
mkdir -p "$FREEZE_DIR"/windows/_internal/ytmusicapi

echo Copy executables to freeze directories
cp "$EXE_PATH" "$FREEZE_DIR"/linux/_internal
cp "$EXE_PATH" "$FREEZE_DIR"/windows/_internal

echo Copy locale files to freeze directories
cp -R "$SITE_PACKAGES"/ytmusicapi/locales "$FREEZE_DIR"/linux/_internal/ytmusicapi
cp -R "$SITE_PACKAGES"/ytmusicapi/locales "$FREEZE_DIR"/windows/_internal/ytmusicapi
