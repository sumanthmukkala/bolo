# Bolo usage — across environments

Bolo is a single CLI (`bolo`) plus optional Claude Code slash commands (`/speak`, `/voice`). Everything you can do via slash commands you can also do via the CLI directly. This doc shows both, organised by environment.

---

## Common controls (regardless of environment)

| Action | What it does |
|---|---|
| **Speak text** | Read provided text aloud now |
| **Read last response** | Re-read whatever the assistant printed in its most recent turn |
| **Toggle auto-read** | Turn the Stop-hook on/off so each new response gets read automatically |
| **Stop audio** | Kill any audio currently playing |
| **Skip next** | Suppress the next single auto-read |
| **Switch voice** | Change the active voice persistently |
| **List voices** | Show all 54 available voices |
| **Sample voice** | Preview a voice without changing the active one |

Below: how to invoke each action in each environment.

---

## Claude Code

The `install.sh` step copies `/speak` and `/voice` slash commands into `~/.claude/commands/`. They are then available in any Claude Code session.

| Action | Slash command |
|---|---|
| Speak text | `/speak <text>` |
| Read last response | `/speak last` |
| Toggle auto-read **on** | `/speak auto on` |
| Toggle auto-read **off** | `/speak auto off` |
| Stop audio | `/speak stop` |
| Skip next | `/speak skip` |
| Show config & quick-ref | `/speak` (no args) |
| Switch voice | `/voice <name>` (e.g. `/voice af_bella`) |
| List voices | `/voice list` |
| Sample voice | `/voice sample <name>` |
| Show current voice | `/voice` (no args) |

For auto-read of every response to fire, you also need to wire the Stop hook in `~/.claude/settings.json` — see [README install steps](../README.md#install).

### Disabling Bolo for one session without uninstalling

Just `/speak auto off`. Bolo stays installed; only auto-read on Stop is suppressed. Inline `/speak <text>` still works.

---

## Hermes

Hermes does not have a native slash-command system that mirrors Claude Code. Two integration options:

### Option 1: Direct CLI invocation in a Hermes skill

Add a Hermes skill at `~/.hermes/skills/bolo.md` (or wherever your Hermes config reads skills from). Skill body:

```markdown
# bolo — speak text aloud via Bolo

When the user says "/speak <text>", "speak <text>", or "read this aloud",
invoke Bolo via Bash:

  ~/.local/share/bolo/bin/bolo "<text>"

To toggle auto-read on / off, modify ~/.local/share/bolo/config.json:

  jq '.auto_read = true'  ~/.local/share/bolo/config.json | sponge ~/.local/share/bolo/config.json
  jq '.auto_read = false' ~/.local/share/bolo/config.json | sponge ~/.local/share/bolo/config.json

To switch voice:

  jq '.active_voice = "<voice_name>"' ~/.local/share/bolo/config.json | sponge ~/.local/share/bolo/config.json
```

### Option 2: Bind to a Hermes Stop event

If your Hermes setup has Stop-event hooks like Claude Code does, point one at `~/.local/share/bolo/bin/stop-hook.sh`. The hook reads the assistant transcript path from stdin (JSON with a `transcript_path` field) — adapt the input format if Hermes provides something different.

---

## Cursor

Cursor's chat panel does not run shell commands directly, but you can:

1. Add a `.cursorrules` file with an instruction telling Cursor to invoke `bolo` via the terminal pane when the user asks for read-aloud.
2. Or just open Cursor's integrated terminal and run `bolo "<text>"` directly.

There is no native auto-read on response in Cursor today (no hook system equivalent to Claude Code's Stop hook). Use Bolo as a manual on-demand reader from the integrated terminal.

---

## Aider, Open Hands, plain CLI agents

Most agentic CLIs let you run shell commands inline. Wrap a Bolo invocation in whatever your tool's "run shell" mechanism is:

```bash
echo "Some text from the agent" | bolo
```

For auto-read of all agent output, pipe the agent's stdout through `tee` and a watcher script that calls `bolo` on each new chunk. This is brittle; the cleanest path is to use Claude Code with the supported Stop-hook integration.

---

## Standalone (no agent)

Bolo is a useful tool on its own:

```bash
# read inline text
bolo "Hello, world."

# read a file
cat article.txt | bolo

# read web content
curl -s https://example.com/article.txt | bolo

# read clipboard (macOS)
pbpaste | bolo

# speed up a long read
bolo --speed 1.4 "$(cat long-document.txt)"

# preview a voice
bolo --voice bm_george "This is George, the British male voice."

# list all voices grouped by language
bolo --list-voices

# version + license info
bolo --version
```

---

## Toggle auto-read from any environment

The single source of truth is `~/.local/share/bolo/config.json`. Any environment that can edit JSON can flip auto-read:

```bash
# turn on
jq '.auto_read = true'  ~/.local/share/bolo/config.json > /tmp/cfg && mv /tmp/cfg ~/.local/share/bolo/config.json

# turn off
jq '.auto_read = false' ~/.local/share/bolo/config.json > /tmp/cfg && mv /tmp/cfg ~/.local/share/bolo/config.json
```

The Stop hook reads this file at every assistant Stop event, so changes take effect on the next response — no daemon restart needed.

---

## Stop audio mid-playback

Bolo plays audio via macOS `afplay`. To kill in-flight playback from any context:

```bash
killall afplay
```

`/speak stop` in Claude Code does exactly this. From your shell, run it directly. From a hotkey, bind it to your terminal or a tool like Karabiner.

---

## Skip the next auto-read once

Sometimes you want the response on screen but not read aloud (long code dump, sensitive content, you are about to step away). Drop a sentinel file that the Stop hook clears on next fire:

```bash
touch ~/.local/share/bolo/skip-next
```

`/speak skip` in Claude Code does this. The next assistant turn skips audio; the turn after returns to normal auto-read.
