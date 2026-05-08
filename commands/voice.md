---
description: Switch the active Bolo voice. `/voice <name>` (e.g. `/voice am_michael`). `/voice list` shows all 54 voices. `/voice sample <name>` plays a preview without changing the active voice.
---

## Your Task

Parse the user's `/voice` arguments:

### Mode 1: `/voice list`

Show all available voices grouped by language and gender:

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --list-voices
```

### Mode 2: `/voice sample <name>`

Generate and play a sample of the named voice without changing the active voice:

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --voice <name> "Hello. This is the <name> voice."
```

### Mode 3: `/voice <name>`

Set the active voice persistently in `$BOLO_HOME/config.json`:

```bash
python3 -c "
import json, os
from pathlib import Path
home = Path(os.environ.get('BOLO_HOME', str(Path.home() / '.local/share/bolo')))
cfg_path = home / 'config.json'
cfg = json.loads(cfg_path.read_text())
cfg['active_voice'] = '<name>'
cfg_path.write_text(json.dumps(cfg, indent=2))
print(f'active_voice = {cfg[\"active_voice\"]}')
"
```

Then play a confirmation sample:

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" "Voice switched to <name>."
```

### Mode 4: `/voice` (no args)

Show current voice and quick reference:

```bash
BOLO_HOME="${BOLO_HOME:-$HOME/.local/share/bolo}"
echo "Current voice: $(jq -r .active_voice "$BOLO_HOME/config.json")"
echo "List voices:   /voice list"
echo "Audition:      /voice sample <name>"
echo "Switch:        /voice <name>"
```

### Voice naming convention

Two-char prefix: `[lang][gender]_`

- `a` American English, `b` British, `h` Hindi, `j` Japanese, `z` Mandarin, `e` Spanish, `f` French, `i` Italian, `p` Portuguese
- `f` female, `m` male

Examples: `am_michael` (American male), `af_bella` (American female), `bm_george` (British male), `hf_alpha` (Hindi female).
