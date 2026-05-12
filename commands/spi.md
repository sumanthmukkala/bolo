---
description: Read text aloud via Bolo with Indian voice (hf_alpha). Local-only wrapper, identical HUD subtitle behavior as /speak. `/spi <text>` reads now. `/spi last` reads your last response. `/spi now` forces read of last. `/spi stop` kills audio. `/spi skip` skips next auto-read. `/spi auto on|off` toggles persistent auto-read pinned to the Indian voice.
---

## Your Task

Parse the user's `/spi` arguments and dispatch through Bolo with the Indian voice override (`hf_alpha`). All audio runs through the same Bolo binary as `/speak`, so the live HUD subtitle works here too.

`SPI_VOICE` defaults to `hf_alpha` (Hindi female; closest Kokoro voice to the previous Mary clone). Alternatives: `hf_beta`, `hm_omega`, `hm_psi`. Change permanently by editing this file.

### Mode 1: `/spi auto on` or `/spi auto off`

Toggle persistent auto-read AND pin the active Bolo voice to Indian so future auto-reads use it.

```bash
python3 -c "
import json, os
from pathlib import Path
home = Path(os.environ.get('BOLO_HOME', str(Path.home() / '.local/share/bolo')))
cfg = home / 'config.json'
data = json.loads(cfg.read_text())
data['auto_read'] = $ON_OR_OFF  # True or False
if $ON_OR_OFF:
    data['active_voice'] = 'hf_alpha'
cfg.write_text(json.dumps(data, indent=2))
print('auto_read =', data['auto_read'], '| active_voice =', data.get('active_voice'))
"
```

### Mode 2: `/spi stop`

Kill any audio currently playing without aborting the running Bolo. For full dead stop, use `/hush`.

```bash
killall afplay 2>/dev/null && echo "✓ silenced" || echo "(nothing playing)"
```

### Mode 3: `/spi skip`

Skip the NEXT auto-read only.

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --skip-next-turn
```

### Mode 4: `/spi last` or `/spi now`

Read your most recent assistant message aloud through Bolo with the Indian voice. stderr → `/dev/tty` so HUD subtitle lands in the user's prompt strip, not in the Bash tool output. Backgrounded so the slash command returns immediately.

```bash
( echo "<your last response text>" | "${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --voice hf_alpha >/dev/null 2>/dev/$(ps -o tty= -p $PPID | tr -d ' ') ) &
```

### Mode 5: `/spi <text>`

Read provided text aloud. stderr → `/dev/tty` so HUD subtitle shows in the prompt strip, not the tool output. Backgrounded.

```bash
( "${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --voice hf_alpha "<text from user>" >/dev/null 2>/dev/$(ps -o tty= -p $PPID | tr -d ' ') ) &
```

### Mode 6: `/spi` (no args)

Show state and quick reference:

```bash
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
echo "=== Bolo config (shared with /speak and /spa) ==="
cat "$BOLO_HOME/config.json"
echo
echo "=== /spi quick reference (Indian voice via Bolo) ==="
echo "  /spi <text>      — speak text now (hf_alpha)"
echo "  /spi last|now    — read last response"
echo "  /spi stop        — kill audio"
echo "  /spi skip        — skip next auto-read"
echo "  /spi auto on|off — toggle auto-read pinned to Indian"
```

### Notes

- Routes through Bolo (Kokoro). HUD subtitle, hush, skip-next-turn, and stop hook auto-read all work identically to `/speak`.
- Voice override is per-invocation via `--voice hf_alpha`. `auto on` also pins it in `config.json` so the stop-hook auto-read uses it.
- Chatterbox MLX daemon, Mary clone, and the old daemon-status / voice-swap modes are removed since Bolo doesn't need them. The Mary `.wav` is still on disk if you ever want to revisit a clone-based pipeline.
- Local-only command. Not pushed anywhere.
