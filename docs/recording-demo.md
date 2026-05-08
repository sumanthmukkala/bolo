# Recording the Bolo demo

A step-by-step script for recording the asciinema demo that goes into the README. Goal: a clean ~30-second cast showing the HUD subtitle in action, ready to embed.

## Pre-flight (do these before you hit record)

```bash
# Install the recorder (one-time)
brew install asciinema

# Optional: tool to render the cast as an inline SVG (no asciinema.org account needed)
npm install -g svg-term-cli

# Resize your Warp/Terminal window to roughly 100 cols × 30 rows.
# Wider is fine, but the SVG looks best at common widths.

# Make sure Bolo is fresh and the voice you want is set.
bolo --version
bolo --voice am_michael "Quick voice check."
killall afplay 2>/dev/null

# Move into the repo (asciinema records cwd in the prompt).
cd ~/Projects/bolo

# Disable auto-read for the recording so YOU control when audio fires.
jq '.auto_read = false' ~/.local/share/bolo/config.json | sponge ~/.local/share/bolo/config.json
```

## What to demonstrate (in order)

The recording should walk through three things in sequence. Each gets ~10 seconds.

1. **One-off speech with the HUD subtitle pinned at the bottom.**
   - Type a sentence directly into bolo.
   - The HUD line writes itself at the bottom of the terminal and rewrites per sentence.
2. **Multi-paragraph text showing pipelined paragraph synthesis.**
   - Pipe a 3-paragraph block in.
   - HUD advances cleanly across paragraph boundaries with no audible gap.
3. **The hush flag silencing playback mid-sentence from another invocation.**
   - Start a long read, then in the same recording (or a side-by-side tab) hit `bolo --hush`.
   - Audio dies within ~50 ms, HUD clears.

## Recording session — exact commands to type

```bash
# Start the recorder. It writes to assets/demo.cast.
asciinema rec assets/demo.cast --idle-time-limit 1.5 --title "Bolo — your terminal talker"

# ---------- Now you are recording. The prompt is yours. Type slowly. ----------

# 1. One-off speech (about 10 seconds)
clear
bolo "Hello. I am Bolo, your terminal talker. The subtitle line below tracks the audio in real time."
# (wait for playback to finish)

# 2. Multi-paragraph (about 10 seconds)
clear
bolo "Bolo is a local TTS for the terminal. It uses Kokoro for the voice.

Each paragraph is synthesised in one call so the prosody flows naturally. The next paragraph is queued up in the background, so there is no gap when one ends and the next begins.

The subtitle stays pinned to the bottom of your terminal and rewrites itself per sentence. It never wraps or scrolls."
# (wait for playback to finish, or hush partway)

# 3. Hush demo (about 10 seconds)
clear
bolo "This is a long sentence that I am going to interrupt mid-flow. Watch the subtitle, watch the audio, and notice how the hush command silences both at the same time, almost instantly." &
sleep 4
bolo --hush
echo "✓ silenced"

# ---------- Stop recording: press Ctrl-D ----------
```

## After recording

```bash
# Preview the cast locally
asciinema play assets/demo.cast

# Re-record if you stumbled — just delete and try again.
rm assets/demo.cast
# (then go back to the asciinema rec line above)
```

## Embedding in the README

You have two paths. Pick one.

### Path A — asciinema.org hosted (simplest, requires free account)

```bash
asciinema upload assets/demo.cast
# Output gives you a URL like https://asciinema.org/a/abc123def
```

Then add to the README near the top, replacing the current "Quick demo" code block:

```markdown
[![asciicast](https://asciinema.org/a/abc123def.svg)](https://asciinema.org/a/abc123def)
```

The image badge plays the cast inline when clicked.

### Path B — Inline SVG (self-hosted, no external dependency)

```bash
svg-term --in assets/demo.cast --out assets/demo.svg --window
```

Then in the README:

```markdown
![Bolo demo](./assets/demo.svg)
```

The SVG renders directly in the GitHub README without an external service. Slightly less interactive (no replay controls), but fully self-contained.

## Final commit + push

```bash
cd ~/Projects/bolo
git add assets/ README.md
git commit -m "Add asciinema demo recording

A ~30-second cast showing the HUD subtitle pinned at the terminal
bottom, multi-paragraph pipelined synthesis with no inter-paragraph
gap, and the --hush flag silencing playback mid-sentence.
"
git push
```

## Cleanup

After recording, restore your normal auto-read setting if you had it on before:

```bash
jq '.auto_read = true' ~/.local/share/bolo/config.json | sponge ~/.local/share/bolo/config.json
```

That's it. You should be done in ~10–15 minutes total including a re-take or two.
