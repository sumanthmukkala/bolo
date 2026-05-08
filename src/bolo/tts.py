#!/usr/bin/env python3
"""Bolo — your terminal talker. Local TTS with a live HUD subtitle synced to playback.

Usage:
  bolo [--voice <name>] [--speed <float>] [--no-play] <text>
  echo "hello" | bolo

Reads voice/speed/HUD config from $BOLO_HOME/config.json (default ~/.local/share/bolo/).
Strips markdown, code blocks, URLs before synthesis.

Project: https://github.com/sumanthmukkala/bolo  •  License: MIT  •  Engine: Kokoro v1.0
"""
from __future__ import annotations
import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

__version__ = "0.1.0"
__name_pretty__ = "Bolo"
__license__ = "MIT"
__engine__ = "Kokoro v1.0"
__url__ = "https://github.com/sumanthmukkala/bolo"

BOLO_HOME = Path(os.environ.get("BOLO_HOME", str(Path.home() / ".local/share/bolo")))
MODELS = BOLO_HOME / "models"
CONFIG_PATH = BOLO_HOME / "config.json"
MODEL = str(MODELS / "kokoro-v1.0.onnx")
VOICES = str(MODELS / "voices-v1.0.bin")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"active_voice": "am_michael", "speed": 1.0, "skip_code_blocks": True, "skip_urls": True}


def clean_text(text: str, cfg: dict) -> str:
    """Strip markdown, code blocks, URLs, etc. before TTS."""
    if cfg.get("skip_code_blocks", True):
        text = re.sub(r"```[\s\S]*?```", " (code block omitted) ", text)
        text = re.sub(r"`[^`]+`", "", text)
    if cfg.get("skip_urls", True):
        text = re.sub(r"https?://\S+", " (link) ", text)
    # Markdown markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    # Tables → drop pipe characters
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"^[-:|\s]+$", "", text, flags=re.MULTILINE)
    # Emoji + decorative box chars
    text = re.sub(r"[🔒🟡🟢🟠🔴⚠️✓✗→←↑↓·•—–]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_paragraphs(text: str) -> list[str]:
    """Split text on blank lines. Paragraph = unit of TTS synthesis (smooth prosody)."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras or ([text.strip()] if text.strip() else [])


def split_sentences(para: str) -> list[str]:
    """Split a paragraph into sentences. Sentence = unit of HUD subtitle advance."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
    return sents or [para]


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Backward-compat shim. Returns one sentence per chunk (used by older callers)."""
    chunks = []
    for para in split_paragraphs(text):
        for sent in split_sentences(para):
            if len(sent) <= max_chars:
                chunks.append(sent)
            else:
                for i in range(0, len(sent), max_chars):
                    chunks.append(sent[i : i + max_chars])
    return chunks


def load_kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(MODEL, VOICES)


def synthesize(kokoro, text: str, voice: str, speed: float, lang: str) -> tuple[Path, float]:
    """Synthesize text → (wav_path, duration_seconds)."""
    import soundfile as sf

    samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    tmp = Path(tempfile.gettempdir()) / f"kokoro-{int(time.time()*1000)}.wav"
    sf.write(str(tmp), samples, sr)
    duration = float(len(samples)) / float(sr)
    return tmp, duration


def play_audio(path: Path) -> None:
    subprocess.run(["afplay", str(path)], check=False)


def split_to_width(text: str, width: int) -> list[str]:
    """Word-aware split into pieces that each fit within `width` characters.

    Used for sub-chunking long sentences so the HUD can show "part 1 → part 2"
    on a single line without ever wrapping or scrolling.
    """
    words = text.split()
    if not words:
        return [text[:width]] if text else [""]
    parts: list[str] = []
    current: list[str] = []
    current_len = 0
    for w in words:
        if len(w) > width:
            if current:
                parts.append(" ".join(current))
                current = []
                current_len = 0
            for i in range(0, len(w), width):
                parts.append(w[i : i + width])
            continue
        sep = 1 if current else 0
        if current_len + sep + len(w) > width and current:
            parts.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += sep + len(w)
    if current:
        parts.append(" ".join(current))
    return parts or [""]


def hud_print(idx: int, total: int, text: str) -> None:
    """Single-line in-place HUD subtitle on stderr.

    Always rewrites the same row via \\r + clear-EOL. Never wraps, never scrolls,
    never migrates upward into the response text. Caller is responsible for
    making sure `text` already fits the terminal width (use split_to_width).

    No LLM call — pure local stderr writes.
    """
    cols = shutil.get_terminal_size((80, 20)).columns or 80
    prefix = f"▶ [{idx}/{total}] "
    body = text.strip().replace("\n", " ")
    avail = max(10, cols - len(prefix) - 1)
    if len(body) > avail:
        cut = body[: avail - 1]
        sp = cut.rfind(" ")
        if sp > avail // 2:
            cut = cut[:sp]
        body = cut.rstrip() + "…"
    sys.stderr.write(f"\r\033[K{prefix}{body}")
    sys.stderr.flush()


def hud_clear() -> None:
    sys.stderr.write("\r\033[K")
    sys.stderr.flush()


def _timing_units(text: str) -> float:
    """Estimated spoken-duration units for a text fragment.

    Combines word count (≈ syllable density) with punctuation pause weights.
    Better correlates with Kokoro's actual playback timing than raw char count,
    which over-weighted long words and under-weighted commas/periods.
    """
    words = len(text.split())
    pause = 0.0
    for ch in text:
        if ch in ".!?":
            pause += 3.8
        elif ch in ",:;":
            pause += 1.8
        elif ch in "—–-":
            pause += 0.7
    return max(1.0, float(words) + pause)


def play_with_sentence_hud(
    wav_path: Path,
    duration: float,
    sentences: list[str],
    sentence_offset: int,
    total_sentences: int,
    hud_enabled: bool,
) -> None:
    """Play wav non-blocking. Advance HUD through single-line sub-chunks of each
    sentence, timed using word-and-punctuation-weighted units within paragraph audio.

    Sub-chunking: if a sentence is longer than the terminal width, it is split
    into multiple width-fitting parts. Each part shows in turn while the audio
    plays through that portion of the sentence. The HUD never wraps or scrolls.
    """
    if not sentences:
        sentences = [""]

    cols = shutil.get_terminal_size((80, 20)).columns or 80
    prefix_len = len(f"▶ [{total_sentences}/{total_sentences}] ")
    avail = max(20, cols - prefix_len - 1)

    # Build flat list of (sentence_idx, part_text, cumulative_units_at_end).
    items: list[tuple[int, str, float]] = []
    cum = 0.0
    for s_idx, sent in enumerate(sentences):
        parts = split_to_width(sent, avail)
        for part in parts:
            cum += _timing_units(part)
            items.append((s_idx, part, cum))
    total_units = cum or 1.0

    # Convert cumulative-units to absolute end-time per item.
    schedule = [(s_idx, part, (c / total_units) * duration) for s_idx, part, c in items]

    proc = subprocess.Popen(["afplay", str(wav_path)])
    start = time.monotonic()
    current = 0
    if hud_enabled and schedule:
        s_idx, part, _ = schedule[0]
        hud_print(sentence_offset + s_idx + 1, total_sentences, part)
    try:
        while proc.poll() is None:
            elapsed = time.monotonic() - start
            while current < len(schedule) - 1 and elapsed >= schedule[current][2]:
                current += 1
                if hud_enabled:
                    s_idx, part, _ = schedule[current]
                    hud_print(sentence_offset + s_idx + 1, total_sentences, part)
            time.sleep(0.05)
    finally:
        proc.wait()


def synthesize_and_play(text: str, voice: str, speed: float, lang: str, play: bool = True) -> Path:
    """Backward-compat wrapper retained for any external callers."""
    kokoro = load_kokoro()
    tmp, _ = synthesize(kokoro, text, voice, speed, lang)
    if play:
        play_audio(tmp)
    return tmp


def _print_banner() -> None:
    print(f"{__name_pretty__} v{__version__} — local TTS with live HUD subtitle")
    print(f"License: {__license__}  •  Engine: {__engine__}  •  {__url__}")


def _list_voices() -> int:
    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        print("kokoro-onnx not installed in this venv. Run install.sh.", file=sys.stderr)
        return 1
    if not Path(MODEL).exists() or not Path(VOICES).exists():
        print(f"Model files missing under {MODELS}. Run install.sh.", file=sys.stderr)
        return 1
    k = Kokoro(MODEL, VOICES)
    voices = list(k.get_voices())
    print(f"{len(voices)} voices available:\n")
    # Group by 2-letter prefix (a*, b*, e*, h*, i*, j*, p*, z*, etc.)
    groups: dict[str, list[str]] = {}
    for v in voices:
        groups.setdefault(v[:2], []).append(v)
    labels = {
        "af": "American female",
        "am": "American male",
        "bf": "British female",
        "bm": "British male",
        "ef": "Spanish female",
        "em": "Spanish male",
        "ff": "French female",
        "hf": "Hindi female",
        "hm": "Hindi male",
        "if": "Italian female",
        "im": "Italian male",
        "jf": "Japanese female",
        "jm": "Japanese male",
        "pf": "Portuguese female",
        "pm": "Portuguese male",
        "zf": "Mandarin female",
        "zm": "Mandarin male",
    }
    for prefix in sorted(groups):
        label = labels.get(prefix, prefix)
        print(f"  {label} ({prefix}*):")
        for v in sorted(groups[prefix]):
            print(f"    - {v}")
        print()
    return 0


def main():
    p = argparse.ArgumentParser(
        prog="bolo",
        description=f"{__name_pretty__} v{__version__} — local TTS with live HUD subtitle. {__license__} licensed.",
    )
    p.add_argument("--voice", help="Override voice from config")
    p.add_argument("--speed", type=float, help="Override speed from config")
    p.add_argument("--no-play", action="store_true", help="Generate audio file but don't play")
    p.add_argument("--lang", default="en-us", help="Language hint (en-us, en-gb, hi)")
    p.add_argument("--list-voices", action="store_true", help="Print all available voices and exit")
    p.add_argument("--hush", action="store_true", help="Kill current audio and skip the next auto-read (silences Bolo from any terminal)")
    p.add_argument("--version", action="version", version=f"{__name_pretty__} {__version__} ({__license__}, engine: {__engine__})")
    p.add_argument("text", nargs="*", help="Text to speak (or pipe via stdin)")
    args = p.parse_args()

    if args.list_voices:
        sys.exit(_list_voices())

    if args.hush:
        subprocess.run(["killall", "afplay"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        skip_flag = BOLO_HOME / "skip-next"
        skip_flag.parent.mkdir(parents=True, exist_ok=True)
        skip_flag.touch()
        print("✓ hushed — audio killed, next auto-read suppressed")
        sys.exit(0)

    cfg = load_config()
    voice = args.voice or cfg.get("active_voice", "am_michael")
    speed = args.speed if args.speed is not None else cfg.get("speed", 1.0)

    # Pick lang from voice prefix unless overridden
    lang = args.lang
    if not args.lang or args.lang == "en-us":
        if voice.startswith("b"):
            lang = "en-gb"
        elif voice.startswith("h"):
            lang = "hi"
        elif voice.startswith("a"):
            lang = "en-us"

    if args.text:
        text = " ".join(args.text)
    else:
        text = sys.stdin.read()

    # Split paragraphs BEFORE cleaning, otherwise whitespace collapse erases blank-line breaks.
    raw_paragraphs = split_paragraphs(text)
    paragraphs = [clean_text(p, cfg) for p in raw_paragraphs]
    paragraphs = [p for p in paragraphs if p.strip()]
    if not paragraphs:
        sys.exit(0)

    para_sentences = [split_sentences(p) for p in paragraphs]
    total_sentences = sum(len(s) for s in para_sentences)

    hud_default = cfg.get("hud", True)
    hud_enabled = hud_default and not args.no_play and sys.stderr.isatty()

    kokoro = load_kokoro()

    # Producer: synth paragraphs in a worker thread so the next paragraph is
    # ready before the current one finishes playing. Eliminates inter-paragraph
    # gaps after the first.
    q: "queue.Queue[tuple[Path, float] | None]" = queue.Queue(maxsize=2)
    producer_err: list[BaseException] = []

    def producer() -> None:
        try:
            for para in paragraphs:
                wav, duration = synthesize(kokoro, para, voice, speed, lang)
                q.put((wav, duration))
        except BaseException as e:
            producer_err.append(e)
        finally:
            q.put(None)

    worker = threading.Thread(target=producer, daemon=True)
    worker.start()

    sentence_offset = 0
    try:
        for sentences in para_sentences:
            item = q.get()
            if item is None:
                break
            wav, duration = item
            if args.no_play:
                sentence_offset += len(sentences)
                continue
            play_with_sentence_hud(
                wav,
                duration,
                sentences,
                sentence_offset,
                total_sentences,
                hud_enabled,
            )
            sentence_offset += len(sentences)
    finally:
        if hud_enabled:
            hud_clear()
        worker.join(timeout=5.0)
        if producer_err:
            raise producer_err[0]


if __name__ == "__main__":
    main()
