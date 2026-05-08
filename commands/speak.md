---
description: Read text aloud via Bolo (local Kokoro TTS with live HUD subtitle). `/speak <text>` reads now. `/speak last` reads your last response. `/speak stop` kills audio. `/speak skip` skips next auto-read once. `/speak auto on|off` toggles persistent auto-read on Stop.
---

## Your Task

Parse the user's `/speak` arguments and dispatch through Bolo. Bolo is a local TTS daemon installed at `$BOLO_HOME` (default `~/.local/share/bolo`).

### Mode 1: `/speak auto on` or `/speak auto off`

Toggle persistent auto-read (responses get spoken automatically when each turn ends).

```bash
python3 -c "
import json, os
from pathlib import Path
home = Path(os.environ.get('BOLO_HOME', str(Path.home() / '.local/share/bolo')))
cfg = home / 'config.json'
data = json.loads(cfg.read_text())
data['auto_read'] = $ON_OR_OFF  # True or False
cfg.write_text(json.dumps(data, indent=2))
print('auto_read =', data['auto_read'])
"
```

### Mode 2: `/speak stop`

Kill any audio currently playing.

```bash
killall afplay 2>/dev/null && echo "✓ silenced" || echo "(nothing playing)"
```

### Mode 2b: `/speak hush`

Kill current audio **and** skip the next auto-read in one go. Useful when you want Bolo silent for the next exchange too, not just the current one.

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --hush
```

### Mode 3: `/speak skip`

Skip the NEXT auto-read only.

```bash
touch "${BOLO_HOME:-$HOME/.local/share/bolo}/skip-next"
echo "✓ next auto-read skipped"
```

### Mode 4: `/speak last`

Read your most recent assistant message aloud right now.

```bash
echo "<your last response text>" | "${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo"
```

### Mode 5: `/speak <text>`

Read provided text aloud:

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" "<text from user>"
```

### Mode 6: `/speak` (no args)

Show state and quick reference:

```bash
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
echo "=== Bolo config ==="
cat "$BOLO_HOME/config.json"
echo
echo "=== Quick reference ==="
echo "  /speak <text>       — speak text now"
echo "  /speak last         — read last response"
echo "  /speak stop         — kill audio"
echo "  /speak skip         — skip next auto-read"
echo "  /speak auto on|off  — toggle auto-read on Stop"
echo "  /voice <name>       — switch voice (am_michael, af_bella, etc.)"
echo "  /voice list         — list all 54 voices"
```

### Notes

- Audio plays through `afplay` (macOS). Cold load ~3–5 s, warm synth sub-second per chunk on M-series.
- Code blocks, URLs, markdown are stripped before synthesis.
- Live HUD subtitle prints below the response while audio plays — no extra tokens used.
- Default voice: `am_michael`. Change with `/voice <name>`.
