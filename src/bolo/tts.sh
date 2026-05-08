#!/usr/bin/env bash
# Bolo wrapper — invokes the Python TTS via the venv created by install.sh.
# Forwards all args + stdin.
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
exec "$BOLO_HOME/venv/bin/python" "$BOLO_HOME/bin/tts.py" "$@"
