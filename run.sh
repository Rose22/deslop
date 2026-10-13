#!/usr/bin/env bash
# -- AI GENERATED CODE (Qwen3.8 Flash Next) :: 2026-10-14
# Entry shim so deslop can be symlinked from anywhere (e.g. ~/bin/deslop).
# Bootstraps a local venv on first run and refreshes deps when requirements.txt changes.

set -euo pipefail

DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
VENV="$DIR/.venv"
STAMP="$VENV/.requirements-stamp"

if [ ! -d "$VENV" ]; then
    echo "deslop: first run - creating venv..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet -r "$DIR/requirements.txt"
elif [ "$DIR/requirements.txt" -nt "$STAMP" ]; then
    echo "deslop: requirements changed - updating deps..."
    "$VENV/bin/pip" install --quiet -r "$DIR/requirements.txt"
fi

touch "$STAMP"
exec "$VENV/bin/python" "$DIR/deslop.py" "$@"
