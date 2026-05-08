# Agent prompt snippet — flowing prose during Bolo auto-read

This is a paste-in instruction for AI assistants so that responses sound natural when Bolo reads them aloud. It is **only relevant if you use a terse-output mode** (Claude Code's caveman plugin, a custom "be brief" system prompt, ultra-concise output preferences, etc.). If your assistant already writes in flowing prose by default, you do not need this.

## What problem this solves

Terse-output modes drop articles ("the", "a"), favour sentence fragments, and skip connective phrases. That style is great for reading on screen — it cuts tokens and noise. But the same text read aloud through TTS sounds staccato and robotic, because spoken English depends on rhythm and connectives that the eye does not need but the ear does.

Bolo's auto-read setting tells you when this matters: if `auto_read: true`, responses will be spoken aloud, so prose style matters; if `auto_read: false`, the user is reading on screen and terse style is fine.

## The snippet

```
When ~/.local/share/bolo/config.json has "auto_read": true, write responses as
flowing prose with complete sentences and natural connectives. Resume terse mode
only when auto_read is false.
```

## Where to paste it

### Claude Code (project-level)

Add to your repo's `CLAUDE.md` near any other behavioural instructions:

```markdown
## Output style

When ~/.local/share/bolo/config.json has "auto_read": true, write responses as
flowing prose with complete sentences and natural connectives. Resume terse mode
only when auto_read is false.
```

### Claude Code (user-level)

Add to `~/.claude/CLAUDE.md` (created if missing):

```markdown
When ~/.local/share/bolo/config.json has "auto_read": true, write responses as
flowing prose with complete sentences and natural connectives. Resume terse mode
only when auto_read is false.
```

### Claude API / generic system prompt

If you build your own assistant via the Anthropic SDK or another provider, append this to your system prompt at session start.

### Cursor, Aider, Open Hands, Hermes, etc.

Most agentic CLIs accept a global rules file (usually a markdown file in the project root or home directory). Paste the snippet into whatever file your tool reads — `.cursorrules`, `.aider.conf.yml`, `~/.hermes/rules.md`, etc.

### Custom CLAUDE.md fragment per division

If you run multiple Claude Code sessions across different vaults or projects (Yantra, Finance, Family, etc.) and only some of them use Bolo, paste the snippet only into those projects' `CLAUDE.md` so terse-mode preferences in other projects are not affected.

## How the assistant should check auto_read state

The assistant should read `~/.local/share/bolo/config.json` (or `$BOLO_HOME/config.json` if `BOLO_HOME` is set) at the start of any turn and inspect the `auto_read` field. A simple bash check:

```bash
jq -r '.auto_read // false' ~/.local/share/bolo/config.json
```

Returns `true` or `false`. Branch output style accordingly.

## Example: combined with caveman

If you use Claude Code's caveman plugin, your full instruction block might look like:

```markdown
## Output style

Default: caveman mode (terse, fragments, drop articles).

Override: when ~/.local/share/bolo/config.json has "auto_read": true, switch to
flowing prose with complete sentences and natural connectives. Resume caveman
when auto_read is false.

Always normal prose for: code, commits, security warnings, irreversible actions.
```

## Why not bake this into Bolo itself

Bolo is a TTS daemon — it reads whatever text it is given. It does not control how the upstream assistant writes. The output-style decision belongs in the assistant's instruction layer, not in the audio-rendering layer. Keeping these separate means Bolo stays a clean drop-in for any text source (assistants, articles, scripts, accessibility readers) regardless of what produced the text.
