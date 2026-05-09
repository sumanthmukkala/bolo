# Bolo launch playbook

Everything you need to ship the public launch in one sitting once the asciinema demo is recorded. Copy-paste-ready post bodies for every channel, plus pre-launch checklist and post-launch response notes.

---

## Pre-launch checklist (before you post anywhere)

- [ ] Asciinema demo recorded and committed to `assets/demo.cast`
- [ ] Demo embedded in README near the top — either via asciinema.org link or inline SVG
- [ ] README requirements section verified accurate
- [ ] `install.sh` runs cleanly on a fresh machine (or you have screenshots showing it does)
- [ ] GitHub repo description matches: "Bolo — your terminal talker. Local Kokoro TTS with live subtitle HUD synced to playback. Mac. MIT."
- [ ] GitHub topics added: `tts`, `kokoro`, `claude-code`, `terminal`, `cli`, `accessibility`, `macos`, `mit-license`
- [ ] You can spend the next 6–12 hours actively responding to comments after posting

To add GitHub topics:

```bash
gh repo edit sumanthmukkala/bolo --add-topic tts,kokoro,claude-code,terminal,cli,accessibility,macos,mit-license
```

---

## Channel 1 — Hacker News (Show HN)

**Where:** https://news.ycombinator.com/submit
**When:** Tuesday or Wednesday, 9–10am Pacific time. Avoid weekends and Mondays.
**Cost:** Free. One try only — do not repost if it flops.

### Title

```
Show HN: Bolo – Local TTS for the terminal with a live subtitle HUD synced to playback
```

### URL

```
https://github.com/sumanthmukkala/bolo
```

### Text body

Leave blank. HN front page favours posts where the URL is the artifact. Your README is the pitch.

### What HN cares about

- Working demo (your asciinema cast — make sure it's at the top of the README)
- Clear technical differentiator (the synced HUD subtitle is yours — most TTS tools don't have that)
- No marketing fluff, no emojis in the title
- Honest about scope and limitations

### Be ready for these questions

- "Why not just use macOS `say`?" — `say` has no HUD, no Kokoro voices, no agent integration. It works for one-off speech, not continuous read-along.
- "How is this different from Whisper / OpenAI TTS?" — Whisper is speech-to-text, not text-to-speech. OpenAI TTS is API-based, costs per token, requires network. Bolo is fully local, $0/month, no API.
- "Why Mac-only?" — v0.1 ships with `afplay` for audio playback. Cross-platform via `sounddevice` is on the roadmap.
- "Is the model open source?" — Yes, Kokoro v1.0 ONNX is MIT-licensed. Credit upstream in the README.

---

## Channel 2 — Reddit

Three subreddits worth posting to. **Do them on the same day as HN, but space them out by 2–3 hours each so you can respond to comments on each one as they come in.** Read each subreddit's rules before posting.

### r/commandline

**URL:** https://www.reddit.com/r/commandline/submit
**Title:**

```
Bolo — local TTS for the terminal with a live subtitle HUD that stays synced to the audio
```

**Body:**

```
I built Bolo because I wanted my terminal AI agents (Claude Code, Hermes, etc.) to read responses aloud while I worked, but I also wanted to glance at the screen and see exactly where the voice was in the response without re-reading from the top.

The unique bit is the HUD subtitle: a single-line caption pinned to the bottom of your terminal that rewrites itself per sentence, synced to the audio playback. It never wraps, never scrolls, never collides with the response above. When the audio ends, the line clears.

Other things worth mentioning:

- Fully local — Kokoro v1.0 ONNX, no API, $0/month, no network
- 54 voices across 9 languages
- Smooth paragraph prosody via paragraph-level synthesis with a producer-consumer queue (no inter-paragraph gaps)
- Word + punctuation-weighted timing for accurate HUD sync
- Tight Claude Code integration: Stop hook auto-reads responses, /speak /voice /hush slash commands
- Works as a plain CLI too — `cat article.md | bolo`, `pbpaste | bolo`, etc.
- Mac-only for v0.1 (Linux/Windows on roadmap), MIT licensed

GitHub: https://github.com/sumanthmukkala/bolo

Built it on my M5 MacBook over a weekend. Feedback welcome.
```

### r/MacApps

**URL:** https://www.reddit.com/r/MacApps/submit
**Title:**

```
[FOSS] Bolo — local TTS for the terminal with live subtitles, $0/mo, no API
```

**Body:**

Use the same body as r/commandline, but lead with the Mac-specific stuff. Add to the top:

```
For Mac terminal users — Bolo runs entirely locally on Apple Silicon (or Intel, slower).
No subscription, no API keys, no network calls after the one-time model download.
```

### r/accessibility (optional but high-value)

**URL:** https://www.reddit.com/r/accessibility/submit
**Title:**

```
Bolo — open-source local TTS for terminal-based developer workflows (free, MIT)
```

**Body:**

Reframe around accessibility specifically. Open with:

```
I built a small open-source tool for low-vision developers and anyone who works in the terminal and wants their output read aloud. It's called Bolo. It's free, MIT-licensed, runs fully offline on Mac, and uses Kokoro for the voice.

Key for accessibility:

- $0/month, no account, no API key
- 54 voices including American/British/Hindi/Mandarin/Spanish/French
- Works with any terminal-based AI assistant (Claude Code, Hermes, Codex CLI, Aider) and also with plain text via stdin
- Live HUD subtitle prints below the response so you can read along visually if you want
- Optional one-keystroke silence via system-wide hotkey (Karabiner snippet in the README)

GitHub: https://github.com/sumanthmukkala/bolo
```

This subreddit is small but highly engaged. People there will share if it solves a real problem.

### r/ClaudeAI (or Claude Code subreddit if one exists)

Search for the active Claude Code community on Reddit. If you find one, post there with focus on the Stop-hook integration:

**Title:**

```
Bolo — Claude Code Stop-hook auto-read with live HUD subtitle (open source, local, free)
```

**Body:** Lead with the slash commands and Stop hook setup. The Claude Code audience already knows what hooks are.

---

## Channel 3 — X (Twitter)

Free account is fine. Skip Premium for the launch.

### Launch thread (5 tweets)

**Tweet 1 — hook + demo**

```
I built Bolo — a local TTS for the terminal with a live subtitle HUD synced to playback.

🔊 Listen to your AI agent (Claude Code, Hermes, Codex) without missing a word
👁 Glance down to see where the voice is in real time
💻 100% local, $0/mo, no API
🆓 MIT, github.com/sumanthmukkala/bolo

[attach demo video]
```

**Tweet 2 — what makes the HUD different**

```
The HUD subtitle is the part I'm most proud of.

Single-line caption pinned to the bottom of your terminal, rewrites itself per sentence, never wraps, never scrolls, never collides with the response above. When audio ends, line clears.

Word + punctuation-weighted timing keeps it tight to the voice.
```

**Tweet 3 — the engine**

```
Powered by Kokoro v1.0 ONNX — 54 voices across 9 languages, fully local on Mac.

Smooth paragraph prosody via paragraph-level synthesis. Producer-consumer queue keeps the next paragraph synthesised while the current one plays, so there are no gaps.

Cold load ~3-5s on M5, sub-second warm.
```

**Tweet 4 — Claude Code integration**

```
Tightest integration is with Claude Code:

/speak <text>     → read text now
/speak auto on    → auto-read every response via Stop hook
/voice <name>     → switch among 54 voices
/hush             → kill audio + skip next, instantly

Also works with Hermes, Aider, Codex CLI, plain pipes (cat | bolo).
```

**Tweet 5 — call to action**

```
Mac-only for v0.1 (Linux/Windows on roadmap). MIT licensed. Built on my M5 over a weekend.

If you live in your terminal and you want your AI to read to you while you work, give it a spin.

🔗 github.com/sumanthmukkala/bolo
```

### Tags to mention

- @AnthropicAI (Claude Code is their product)
- @hexgrad (Kokoro upstream author, if findable)
- @thewh1teagle (kokoro-onnx author)
- Any Claude Code community managers

---

## Channel 4 — Awesome lists (long tail SEO)

Submit PRs to these `awesome-*` lists adding Bolo:

- https://github.com/anthropics/claude-code (if they have an awesome list)
- https://github.com/agarrharr/awesome-cli-apps
- https://github.com/aleksandar-todorovic/awesome-c (look for terminal section)
- https://github.com/iCHAIT/awesome-macOS
- https://github.com/brunoborges/awesome-tts (if exists)
- https://github.com/keon/awesome-nlp (TTS section)

PR template:

```markdown
Add Bolo — local TTS for the terminal with a live subtitle HUD synced to playback. Mac, MIT, 54 voices via Kokoro v1.0 ONNX, deep Claude Code integration.

Repo: https://github.com/sumanthmukkala/bolo
```

Each PR takes ~3 minutes. Low immediate traffic, compounds over months as discovery channel.

---

## Channel 5 — Product Hunt (optional)

**URL:** https://www.producthunt.com/posts/new
**When:** Launch Tuesday for max visibility. Best between 12:01am and 8am Pacific.

**Tagline:**

```
Local TTS for your terminal — voice + live subtitles, no API
```

**Description:**

```
Bolo reads your terminal output aloud through a fully-local Kokoro TTS model, with a live single-line subtitle pinned to the bottom that stays synced to the audio. Built primarily for terminal-native AI agents (Claude Code, Hermes, Codex CLI) but works with any text source. 54 voices, 9 languages, MIT, $0/month, Mac.
```

PH skews less technical than HN. Worth a launch but not the centerpiece.

---

## Channel 6 — Anthropic community

Wherever the Claude Code community lives — Discord, Slack, Reddit, official forum. Bolo's deep Claude Code integration is your strongest differentiator there. Anthropic developer relations may amplify if they notice.

Worth checking:
- https://github.com/anthropics/claude-code (issues / discussions if open)
- Anthropic Discord (if you find an invite link)
- The community Slack/Discord

---

## After launch — response playbook

For the first 6–12 hours after each post, monitor and respond. Momentum compounds; silence kills threads.

### Common questions and responses

**"Does it work on Linux/Windows?"**

> Mac only for v0.1. Linux and Windows are on the roadmap — the only blocker is replacing afplay with sounddevice, which is straightforward but I haven't done it yet.

**"What's the model size?"**

> Kokoro v1.0 ONNX is ~310 MB, plus a 28 MB voices file. Downloaded once during install. After that, fully offline.

**"How is the latency?"**

> Cold load ~3-5s on M-series, sub-second warm synthesis per paragraph. Time to first audio is gated by synthesis, not network.

**"Can it stream / play before synth completes?"**

> Not yet. Each paragraph synthesises in one Kokoro call before playback starts. Streaming is on the roadmap.

**"Why a HUD subtitle instead of full-screen?"**

> Pinned single-line subtitle keeps the response above untouched. Multi-line wrapping caused the HUD to migrate upward into the response on every sentence change. Single line + word-aware truncate sidesteps the issue.

**"Is the audio quality good?"**

> Yes. Kokoro v1.0 is best-in-class for the size — 82M params, sounds remarkably natural. Pick `am_michael` or `bm_george` for neutral male, `af_bella` for clear female. Try `/voice list` to see all 54.

### Engagement tips

- Reply to every substantive comment within an hour for the first 6 hours.
- "Thanks!" alone is not enough — say what you'll do with the feedback.
- If someone reports a bug, file a GitHub issue and link it from your reply.
- If someone proposes a feature, decide quickly: roadmap, no, or "depends" — and say so.
- Don't argue with critics. Acknowledge the point, link to your reasoning if it's already in the README, move on.

---

## What success looks like

For a niche local TTS tool:

- **First 24 hours:** 100–500 GitHub stars from a successful HN landing
- **First week:** 1k–3k stars, 50–100 issues/discussions, a few PRs
- **First month:** organic discovery via awesome-lists kicks in, steady ~10–30 stars/day
- **First 3 months:** community starts asking for Linux/Windows port — that's when you decide whether to invest

If HN and Reddit don't take, you'll see ~10–50 stars and that's fine. The tool exists, MIT-licensed, on GitHub. People will find it via search when they need it. Slow steady discovery is also a real outcome.

---

## What NOT to do

- Don't pay for X Premium yet. Wait until you decide if you're committing to ongoing posting.
- Don't post the same launch on multiple subreddits simultaneously without spacing — looks spammy.
- Don't post on Hacker News more than once per week from the same account (gets penalized).
- Don't message strangers asking them to upvote. HN/Reddit detect this and penalize.
- Don't include emojis in the HN title.
- Don't post on Friday afternoon or weekends — traffic is dead.
- Don't disable comments anywhere. The conversation is the value.

---

## Day-of launch sequence

Suggested timeline for one launch day (Tuesday):

| Time (Pacific) | Action |
|---|---|
| 8:30 am | Final pre-launch check, demo plays correctly, README looks good |
| 9:00 am | Submit Show HN |
| 9:30 am | Post r/commandline |
| 10:30 am | Post r/MacApps |
| 11:30 am | Post r/accessibility |
| 12:00 pm | Post X launch thread |
| 12:30 pm | Submit Product Hunt |
| 1:00 pm onward | Respond to all comments aggressively |
| 4:00 pm | First check-in on each channel, reply to anything new |
| 7:00 pm | Final check-in for the day, schedule next-day responses |

Total active time: about 4-6 hours of focused posting + responding. The rest of the day, the channels do the work.
