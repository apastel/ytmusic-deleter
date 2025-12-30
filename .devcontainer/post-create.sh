#!/bin/bash
set -e  # Fail fast
/workspaces/ytmusic-deleter/.venv/bin/python3 -m pre_commit install
pdm fbs run
