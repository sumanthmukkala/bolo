#!/usr/bin/env bash
# Bolo Stop hook for Claude Code.
#
# Runs after each assistant turn. If auto_read=true in $BOLO_HOME/config.json,
# pipes the last assistant message into Bolo and plays it with the live HUD.
#
# Wire it up by adding this script's path to the "Stop" hooks array in
# ~/.claude/settings.json. install.sh prints the snippet for you.

set -uo pipefail

BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
CFG="$BOLO_HOME/config.json"
TTS_CMD="$BOLO_HOME/bin/bolo"
SKIP_FLAG="$BOLO_HOME/skip-next"
LOG="$BOLO_HOME/stop-hook.log"

# Bail out if Bolo isn't installed or auto-read is disabled.
[ -f "$CFG" ] || exit 0
[ -x "$TTS_CMD" ] || exit 0
[ "$(jq -r '.auto_read // false' "$CFG" 2>/dev/null)" = "true" ] || exit 0

# Honour one-shot skip — clear flag and exit silently.
if [ -f "$SKIP_FLAG" ]; then
  rm -f "$SKIP_FLAG"
  exit 0
fi

# Read transcript path from hook stdin payload.
input=$(cat)
transcript_path=$(printf '%s' "$input" | jq -r '.transcript_path // empty')
[ -z "$transcript_path" ] && exit 0
[ -f "$transcript_path" ] || exit 0

# Brief sync wait — transcript flush + filesystem visibility.
sleep 0.3

# Pull the LAST assistant text block.
last_text=$(jq -rs '
  [.[] | select(.type=="assistant")
    | (.message.content // [])
    | map(select(.type=="text") | .text)
    | join(" ")
  ]
  | map(select(length > 0))
  | last // ""
' "$transcript_path" 2>/dev/null)

[ -z "$last_text" ] && exit 0

# Speak in background so the Stop hook returns immediately.
# stderr → user's actual tty (walked up process tree) so HUD subtitle shows.
# Stop hooks run without a controlling terminal, so /dev/tty fails outright —
# fall back to /dev/null (audio still plays) if no ancestor pty found.
find_user_tty() {
  local pid=$PPID
  while [ -n "$pid" ] && [ "$pid" != "1" ]; do
    local tty
    tty=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')
    if [ -n "$tty" ] && [ "$tty" != "?" ] && [ "$tty" != "??" ]; then
      echo "/dev/$tty"
      return 0
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
  done
  echo "/dev/null"
}
HUD_OUT=$(find_user_tty)
( printf '%s' "$last_text" | "$TTS_CMD" >/dev/null 2>"$HUD_OUT" ) &

# Log (truncated to last ~50 entries).
{
  printf '=== %s ===\n' "$(date '+%F %T')"
  printf 'transcript: %s\n' "$transcript_path"
  printf 'spoken (first 80 chars): %s\n\n' "${last_text:0:80}"
} >> "$LOG" 2>/dev/null

if [ -f "$LOG" ]; then
  tail -200 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi

exit 0
