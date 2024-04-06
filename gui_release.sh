#!/bin/bash
set -e

VENV_PATH=$PDM_PROJECT_ROOT/.venv
echo $PDM_PROJECT_ROOT
VENV_BIN=bin
EXE_PATH=$VENV_PATH/$VENV_BIN/ytmusic-deleter
FREEZE_DIR=$PDM_PROJECT_ROOT/gui/src/freeze

# Activate the virtual environment
source "$VENV_PATH/$VENV_BIN/activate"

# Get the site-packages directory
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")

pdm install --no-editable
mkdir -p $FREEZE_DIR/linux/_internal/ytmusicapi
mkdir -p $FREEZE_DIR/windows/_internal/ytmusicapi
cp $EXE_PATH $FREEZE_DIR/linux/_internal
cp $EXE_PATH $FREEZE_DIR/windows/_internal
cp -R $SITE_PACKAGES/ytmusicapi/locales $FREEZE_DIR/linux/_internal/ytmusicapi
cp -R $SITE_PACKAGES/ytmusicapi/locales $FREEZE_DIR/windows/_internal/ytmusicapi
