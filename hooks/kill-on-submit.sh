#!/usr/bin/env bash
# Kill any in-flight Kokoro TTS playback whenever user submits a new prompt.
# Rationale: /speak stop queues behind current Claude turn; typing kills audio instantly.
killall afplay 2>/dev/null
exit 0
