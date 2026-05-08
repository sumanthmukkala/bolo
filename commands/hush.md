---
description: `/hush` — full dead stop on current Bolo playback. `/hush para` — skip current paragraph, continue with rest. Does not affect next assistant turn (use /speak skip for that).
---

## Your Task

Parse the user's `/hush` argument and dispatch.

### Mode 1: `/hush` (no args)

Full dead stop. Kill audio + abort the running Bolo process. Does NOT touch the next assistant turn.

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --hush
```

### Mode 2: `/hush para` (or `/hush skip`)

Skip the current paragraph; let Bolo continue with the rest of the response.

```bash
"${BOLO_HOME:-$HOME/.local/share/bolo}/bin/bolo" --skip-paragraph
```

### Notes

- `/hush` only affects the **currently-playing** response. To suppress the **next** assistant turn's auto-read, use `/speak skip` instead.
- Works from any terminal: `bolo --hush` and `bolo --skip-paragraph` are the standalone equivalents.
