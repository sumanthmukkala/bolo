#!/usr/bin/env bash
# Non-interactive Bolo demo for asciinema recording.
# Run via: asciinema rec assets/demo.cast --command "bash scripts/demo-script.sh" --idle-time-limit 2

set -uo pipefail

BOLO="${BOLO:-$HOME/.local/share/bolo/bin/bolo}"

banner() {
  cat <<'EOF'
══════════════════════════════════════════════════════════
  Bolo — your terminal talker
  Local TTS for the terminal with a live subtitle HUD
══════════════════════════════════════════════════════════
EOF
}

# ---- Segment 1 — single sentence ----
clear
banner
echo
echo '$ bolo "Hello. I am Bolo, your terminal talker."'
sleep 0.8
"$BOLO" "Hello. I am Bolo, your terminal talker."
sleep 1.0

# ---- Segment 2 — multi-paragraph ----
clear
banner
echo
echo '$ bolo "Multi-paragraph mode — pipelined synthesis, no gaps."'
sleep 0.8
"$BOLO" "Bolo is a local TTS for the terminal. It uses Kokoro for the voice. Each paragraph is synthesised in one call so the prosody flows naturally.

The subtitle stays pinned to the bottom of your terminal and rewrites itself per sentence. It never wraps or scrolls."
sleep 1.0

# ---- Segment 3 — hush demo ----
clear
banner
echo
echo '$ bolo "Long sentence to interrupt..." &'
echo '$ bolo --hush     # in another terminal'
sleep 0.8
"$BOLO" "This is a long sentence that I am about to interrupt mid-flow, just to show the hush flag in action across terminals." &
BOLO_PID=$!
sleep 3.5
"$BOLO" --hush
wait "$BOLO_PID" 2>/dev/null
sleep 0.5
echo

# ---- Outro ----
clear
banner
echo
echo "  github.com/sumanthmukkala/bolo"
echo "  MIT  •  Mac  •  54 voices  •  \$0/month"
echo
sleep 2.0
