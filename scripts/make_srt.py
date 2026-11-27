#!/usr/bin/env python3
"""Build an SRT subtitle file from per-scene narration (WAV + TXT pairs).

Usage:
  make_srt.py --audio dir --text dir [--out subs.srt] [--pad 0.0]
  # expects sceneNN.wav next to sceneNN.txt (same stem)
Timing: each scene lasts its WAV duration (+pad); text chunks are
allocated proportionally by character count. Chunks split at ।?! , — .
Exit: 0 = written + validated (ordered cues), 1 = fail.
"""
import argparse
import re
import sys
import wave
from pathlib import Path


def wav_dur(p: Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / w.getframerate()


def ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chunks(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[।?!])\s+|(?<=,)\s+|(?<=—)\s+|(?<=\.)\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    out: list[str] = []
    for p in parts:
        if out and (len(out[-1]) + len(p) < 60 or len(p) < 15):
            out[-1] = out[-1] + " " + p
        elif len(p) > 110:
            mid = p.find(",", 40)
            if mid < 0:
                mid = len(p) // 2
            out += [p[:mid].strip(), p[mid:].strip()]
        else:
            out.append(p)
    return out or [text]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", default="subtitles.srt")
    ap.add_argument("--pad", type=float, default=0.0,
                    help="extra seconds per scene (0 when clip length = audio)")
    args = ap.parse_args()

    audio_dir, text_dir = Path(args.audio), Path(args.text)
    wavs = sorted(audio_dir.glob("*.wav"))
    if not wavs:
        print("no .wav files found", file=sys.stderr)
        return 1

    entries: list[tuple[float, float, str]] = []
    clock = 0.0
    used = 0
    for w in wavs:
        txt = text_dir / (w.stem + ".txt")
        if not txt.exists():
            print(f"skip {w.name} (no {txt.name})", file=sys.stderr)
            continue
        dur = wav_dur(w) + args.pad
        cs = chunks(txt.read_text(encoding="utf-8"))
        weights = [max(len(c), 1) for c in cs]
        tw = sum(weights)
        t = clock
        for c, wd in zip(cs, weights):
            d = dur * wd / tw
            entries.append((t, min(t + d, clock + dur), c))
            t += d
        clock += dur
        used += 1

    if not entries:
        print("no wav+txt pairs matched", file=sys.stderr)
        return 1

    # validation: strictly non-overlapping, ascending
    for i in range(len(entries) - 1):
        if entries[i][1] > entries[i + 1][0] + 1e-6:
            print(f"overlap at cue {i + 1}", file=sys.stderr)
            return 1

    lines: list[str] = []
    for n, (a, b, txt) in enumerate(entries, 1):
        lines += [str(n), f"{ts(a)} --> {ts(b)}", txt, ""]
    out = Path(args.out)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} — {len(entries)} cues from {used} scene(s), "
          f"ends {int(clock // 60)}:{int(clock % 60):02d} ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
