#!/usr/bin/env python3
"""vs_music.py - synthesize a gentle, melodic background track for Reels.

Not a flat sine wave: a soft chord pad (warm triangle-ish tones) with a
slow arpeggio and a subtle pulse. Outputs WAV; ffmpeg converts to m4a.
Tunable length (loops naturally). Ideal for educational Reels.

Usage:
  vs_music.py --out music.wav [--seconds 60] [--tempo 96]
Exit: 0 ok.
"""
import argparse
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100


def note(freq, t, sr=SR, attack=0.02, decay=0.18, sustain=0.7, volume=0.3):
    """Soft plucked note with ADSR-ish envelope."""
    n = int(t * sr)
    env = np.ones(n)
    a = max(1, int(attack * sr))
    d = max(1, int((1 - sustain) * decay * sr))
    env[:a] = np.linspace(0, 1, a)
    env[a:a + d] = np.linspace(1, sustain, d)
    env[a + d:] = sustain * np.exp(-np.linspace(0, 6, n - a - d))
    wave_ = (np.sin(2 * np.pi * freq * np.arange(n) / sr)
             + 0.4 * np.sin(4 * np.pi * freq * np.arange(n) / sr))
    return (wave_ * env * volume).astype(np.float64)


def pad(freqs, t, sr=SR, volume=0.35):
    """Soft sustained pad (sum of detuned sines)."""
    n = int(t * sr)
    buf = np.zeros(n)
    for f in freqs:
        buf += np.sin(2 * np.pi * f * np.arange(n) / sr)
        buf += np.sin(2 * np.pi * (f * 1.005) * np.arange(n) / sr) * 0.5
    env = np.ones(n)
    a = int(0.3 * sr)
    env[:a] = np.linspace(0, 1, a)
    env[-int(0.4 * sr):] = np.linspace(1, 0, int(0.4 * sr))
    return (buf / len(freqs) * volume * env).astype(np.float64)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="music.wav")
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--tempo", type=float, default=96.0)
    args = ap.parse_args()

    # Am - F - C - G chord progression (frequencies)
    chords = [
        [220.00, 261.63, 329.63],   # Am (A C E)
        [174.61, 220.00, 261.63],   # F  (F A C)
        [261.63, 329.63, 392.00],   # C  (C E G)
        [196.00, 246.94, 293.66],   # G  (G B D)
    ]
    beat = 60.0 / args.tempo
    chord_dur = beat * 4  # one chord per bar
    total = int(args.seconds * SR)
    out = np.zeros(total)

    bar = 0
    pos = 0
    while pos < total:
        chord = chords[bar % len(chords)]
        seg = int(min(chord_dur * SR, total - pos))
        # pad layer
        out[pos:pos + seg] += pad(chord, seg / SR, volume=0.30)[:seg]
        # arpeggio: 8th notes, soft plucks
        for i in range(8):
            ptime = i * beat / 2
            idx = int(ptime * SR)
            if pos + idx + int(0.5 * SR) > total:
                break
            note_freq = chord[i % len(chord)] * 2
            out[pos + idx:pos + idx + int(0.5 * SR)] += \
                note(note_freq, 0.5, volume=0.10)[:int(0.5 * SR)]
        # subtle bass pulse on beat
        bass_idx = int(0.0 * SR)
        if pos + bass_idx + int(0.4 * SR) < total:
            out[pos + bass_idx:pos + bass_idx + int(0.4 * SR)] += \
                note(chord[0] / 2, 0.4, volume=0.14)[:int(0.4 * SR)]
        pos += seg
        bar += 1

    # normalize + soft limit
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.85
    out = np.clip(out, -0.95, 0.95)
    pcm = (out * 32767).astype(np.int16)

    path = Path(args.out)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {path} — {args.seconds:.0f}s, {path.stat().st_size // 1024} KB")

    # convenience: convert to m4a if requested implicitly (same stem)
    m4a = path.with_suffix(".m4a")
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ff, "-y", "-i", str(path), "-c:a", "aac", "-b:a",
                        "128k", str(m4a)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"wrote {m4a} — {m4a.stat().st_size // 1024} KB")
    except Exception as e:
        print(f"m4a conversion skipped: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
