---
description: Read text aloud via Bolo with American voice (am_puck). Local-only wrapper, identical HUD subtitle behavior as /speak. `/spa <text>` reads now. `/spa last` reads your last response. `/spa now` forces read of last. `/spa stop` kills audio. `/spa skip` skips next auto-read. `/spa auto on|off` toggles persistent auto-read pinned to the American voice.
---

## Your Task

Parse the user's `/spa` arguments and dispatch through Bolo with the American voice override (`am_puck`). All audio runs through the same Bolo binary as `/speak`, so the live HUD subtitle works here too.

`SPA_VOICE` defaults to `am_puck`. To change permanently, edit this file or use `/voice <name>` after a /spa invocation.

### Mode 1: `/spa auto on` or `/spa auto off`

Toggle persistent auto-read AND pin the active Bolo voice to American so future auto-reads use it.

```bash
python3 -c "
import json, os
from pathlib import Path
home = Path(os.environ.get('BOLO_HOME', str(Path.home() / '.local/share/bolo')))
cfg = home / 'config.json'
data = json.loads(cfg.read_text())
data['auto_read'] = $ON_OR_OFF  # True or False
if $ON_OR_OFF:
    data['active_voice'] = 'am_puck'
cfg.write_text(json.dumps(data, indent=2))
print('auto_read =', data['auto_read'], '| active_voice =', data.get('active_voice'))
"
```

### Mode 2: `/spa stop`

Kill any audio currently playing without aborting the running Bolo. For full dead stop, use `/hush`.

```bash
killall afplay 2>/dev/null && echo "✓ silenced" || echo "(nothing playing)"
```

### Mode 3: `/spa skip`

Skip the NEXT auto-read only.

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --skip-next-turn
```

### Mode 4: `/spa last` or `/spa now`

Read your most recent assistant message aloud through Bolo with the American voice. stderr → `/dev/tty` so HUD subtitle lands in the user's prompt strip, not in the Bash tool output. Backgrounded so the slash command returns immediately.

```bash
( echo "<your last response text>" | "${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --voice am_puck >/dev/null 2>/dev/$(ps -o tty= -p $PPID | tr -d ' ') ) &
```

### Mode 5: `/spa <text>`

Read provided text aloud. stderr → `/dev/tty` so HUD subtitle shows in the prompt strip, not the tool output. Backgrounded.

```bash
( "${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --voice am_puck "<text from user>" >/dev/null 2>/dev/$(ps -o tty= -p $PPID | tr -d ' ') ) &
```

### Mode 6: `/spa` (no args)

Show state and quick reference:

```bash
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
echo "=== Bolo config (shared with /speak and /spi) ==="
cat "$BOLO_HOME/config.json"
echo
echo "=== /spa quick reference (American voice via Bolo) ==="
echo "  /spa <text>      — speak text now (am_puck)"
echo "  /spa last|now    — read last response"
echo "  /spa stop        — kill audio"
echo "  /spa skip        — skip next auto-read"
echo "  /spa auto on|off — toggle auto-read pinned to American"
```

### Notes

- Routes through Bolo. HUD subtitle, hush, skip-next-turn, and stop hook auto-read all work identically to `/speak`.
- Voice override is per-invocation via `--voice am_puck`. `auto on` also pins it in `config.json` so the stop-hook auto-read uses it.
- Local-only command. Not pushed anywhere.
