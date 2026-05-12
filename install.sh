#!/usr/bin/env bash
# Bolo installer — Mac edition.
#
# Sets up a venv, installs Python deps, downloads the Kokoro ONNX model files,
# copies slash commands into ~/.claude/commands/, and (optionally) wires up the
# Claude Code Stop hook so responses get auto-read with the live HUD subtitle.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

KOKORO_MODEL_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

say() { printf '\033[1;36m▸\033[0m %s\n' "$*"; }
ok()  { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn(){ printf '\033[1;33m!\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# ---------- Sanity checks ----------
[[ "$(uname -s)" == "Darwin" ]] || die "Bolo v0.1 ships Mac-only. Linux/Windows support is on the roadmap."
command -v afplay  >/dev/null   || die "afplay not found. Are you on macOS?"
command -v curl    >/dev/null   || die "curl not found."

# Find a Python ≥3.10. Try specific versions first, fall back to plain python3.
PYTHON=""
for cand in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1; then
    ver="$("$cand" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if [[ "$(printf '%s\n' "3.10" "$ver" | sort -V | head -1)" == "3.10" ]]; then
      PYTHON="$cand"
      PY_MAJOR_MINOR="$ver"
      break
    fi
  fi
done
[[ -n "$PYTHON" ]] || die "Python 3.10+ not found. Install via Homebrew: brew install python@3.12"
ok "Python $PY_MAJOR_MINOR found at $(command -v "$PYTHON")"

say "Bolo home will be at: $BOLO_HOME"
mkdir -p "$BOLO_HOME"/{models,bin}

# ---------- Venv + Python deps ----------
if [[ ! -d "$BOLO_HOME/venv" ]]; then
  say "Creating venv..."
  "$PYTHON" -m venv "$BOLO_HOME/venv"
fi
ok "venv ready"

say "Installing Python dependencies..."
"$BOLO_HOME/venv/bin/pip" install --upgrade pip >/dev/null
"$BOLO_HOME/venv/bin/pip" install kokoro-onnx soundfile numpy >/dev/null
ok "dependencies installed"

# ---------- Kokoro model files ----------
download_if_missing() {
  local url="$1" dest="$2" name="$3"
  if [[ -f "$dest" ]]; then
    ok "$name already present"
    return
  fi
  say "Downloading $name (this is a one-time, ~300 MB combined)..."
  curl -L --fail --progress-bar "$url" -o "$dest"
  ok "$name downloaded"
}
download_if_missing "$KOKORO_MODEL_URL"  "$BOLO_HOME/models/kokoro-v1.0.onnx"  "Kokoro model"
download_if_missing "$KOKORO_VOICES_URL" "$BOLO_HOME/models/voices-v1.0.bin"   "Kokoro voices"

# ---------- Copy + wire scripts ----------
say "Installing scripts..."
cp "$REPO_DIR/src/bolo/tts.py"  "$BOLO_HOME/bin/tts.py"
cp "$REPO_DIR/src/bolo/tts.sh"  "$BOLO_HOME/bin/bolo"
cp "$REPO_DIR/hooks/stop-hook.sh"      "$BOLO_HOME/bin/stop-hook.sh"
cp "$REPO_DIR/hooks/kill-on-submit.sh" "$BOLO_HOME/bin/kill-on-submit.sh" 2>/dev/null || true
chmod +x "$BOLO_HOME/bin/"*
ok "scripts installed at $BOLO_HOME/bin"

# ---------- Default config ----------
if [[ ! -f "$BOLO_HOME/config.json" ]]; then
  cat > "$BOLO_HOME/config.json" <<'JSON'
{
  "active_voice": "am_michael",
  "auto_read": false,
  "speed": 1.0,
  "skip_code_blocks": true,
  "skip_urls": true,
  "max_chars_per_chunk": 250,
  "hud": true
}
JSON
  ok "default config written to $BOLO_HOME/config.json"
fi

# ---------- Claude Code slash commands ----------
if [[ -d "$CLAUDE_DIR" ]]; then
  say "Installing Claude Code slash commands into $CLAUDE_DIR/commands/..."
  mkdir -p "$CLAUDE_DIR/commands"
  cp "$REPO_DIR/commands/"*.md "$CLAUDE_DIR/commands/"
  ok "slash commands installed (/speak, /spa, /spi, /voice, /hush)"
else
  warn "Claude Code dir ($CLAUDE_DIR) not found — skipping slash command install."
fi

# ---------- Claude Code Stop hook (optional) ----------
HOOK_PATH="$BOLO_HOME/bin/stop-hook.sh"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [[ -f "$SETTINGS_FILE" ]]; then
  if ! grep -q "$HOOK_PATH" "$SETTINGS_FILE" 2>/dev/null; then
    printf '\n'
    read -r -p "$(printf '\033[1;36m?\033[0m Wire Bolo as a Claude Code Stop hook so responses auto-read? [y/N] ')" reply
    if [[ "$reply" =~ ^[Yy]$ ]]; then
      warn "Manual step: add this entry to the 'Stop' array in $SETTINGS_FILE:"
      printf '  {\n    "hooks": [\n      { "type": "command", "command": "%s" }\n    ]\n  }\n' "$HOOK_PATH"
    fi
  else
    ok "Stop hook already wired in $SETTINGS_FILE"
  fi
fi

# ---------- Done ----------
printf '\n'
ok "Bolo v0.1.0 installed."
printf '\n'
printf 'Try it now:\n'
printf '  echo "Hello from Bolo." | %s/bin/bolo\n' "$BOLO_HOME"
printf '\n'
printf 'List voices:\n'
printf '  %s/bin/bolo --list-voices\n' "$BOLO_HOME"
printf '\n'
printf 'Add to PATH (optional):\n'
printf '  echo '"'"'export PATH="%s/bin:$PATH"'"'"' >> ~/.zshrc\n' "$BOLO_HOME"
printf '\n'
printf 'In Claude Code: /speak, /spa, /spi, /voice, /hush slash commands are ready.\n'
printf 'Docs: %s/README.md\n' "$REPO_DIR"
