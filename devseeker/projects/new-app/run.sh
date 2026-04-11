#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pytest &
TEST_PID=$!

python -m src.main &
GAME_PID=$!

wait "$TEST_PID"
wait "$GAME_PID"
