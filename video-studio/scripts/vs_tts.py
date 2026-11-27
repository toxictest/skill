#!/usr/bin/env python3
"""Synthesize per-scene narration audio and write real durations into the manifest.

Backends:
  edge     Microsoft Edge TTS — free, no API key (pip install edge-tts)
  silent   deterministic silent WAV (offline / self-test)
  cmd      any local TTS CLI via --cmd 'my-tts -o {out} {text}' ({out}/{text} filled in)

Usage:
  vs_tts.py scene_manifest.json --out-audio narration/  [--engine edge]
                                  [--voice en-US-JennyNeural] [--rate +0%]
                                  [--cmd 'my-tts -o {out} {text}']
Updates manifest in place: each scene gets "audio" path and "duration" = real seconds.
Exit: 0 ok, 1 on failure.
"""
import argparse
import asyncio
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path


def ff() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def silent_wav(path: Path, seconds: float, rate: int = 24000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", 0)
                               for _ in range(int(rate * seconds))))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


async def edge_synth(text: str, out: Path, voice: str, rate: str) -> None:
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(str(out))


def synth_edge(text: str, out: Path, voice: str, rate: str) -> None:
    try:
        asyncio.run(edge_synth(text, out, voice, rate))
    except Exception as e:  # network or service issues → clear message
        raise RuntimeError(f"edge-tts failed ({e}); retry with --engine silent "
                           f"or install: pip install edge-tts") from e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out-audio", default="narration")
    ap.add_argument("--engine", choices=["edge", "silent", "cmd"], default="edge")
    ap.add_argument("--voice", default="en-US-JennyNeural")
    ap.add_argument("--rate", default="+0%", help="edge-tts rate, e.g. '+5%'")
    ap.add_argument("--cmd", default=None, help="custom TTS command template")
    ap.add_argument("--no-update", action="store_true",
                    help="only render audio, do not rewrite manifest")
    args = ap.parse_args()

    mpath = Path(args.manifest)
    if not mpath.exists():
        print(f"not found: {mpath}", file=sys.stderr)
        return 1
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    audio_dir = Path(args.out_audio)
    audio_dir.mkdir(parents=True, exist_ok=True)

    for sc in manifest["scenes"]:
        idx = sc["index"]
        wav = audio_dir / f"scene_{idx:02d}.wav"
        text = sc["narration"]
        if not text.strip():
            print(f"scene {idx}: empty narration — skipped", file=sys.stderr)
            continue
        if args.engine == "silent":
            est = sc.get("duration") or 3.0
            silent_wav(wav, est)
        elif args.engine == "cmd":
            if not args.cmd:
                print("--engine cmd needs --cmd 'template'", file=sys.stderr)
                return 1
            cmd = args.cmd.replace("{out}", str(wav)).replace("{text}", text)
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0 or not wav.exists():
                print(f"scene {idx}: TTS cmd failed: {r.stderr[-200:]}", file=sys.stderr)
                return 1
        else:
            try:
                synth_edge(text, wav, args.voice, args.rate)
            except RuntimeError as e:
                print(e, file=sys.stderr)
                return 1
        # normalize to mono 16-bit 44.1k WAV via bundled ffmpeg (mp3/ogg safe)
        ffmpeg = ff()
        tmp = wav.with_suffix(".tmp.wav")
        r = subprocess.run([ffmpeg, "-y", "-i", str(wav), "-ac", "1", "-ar", "44100",
                            "-c:a", "pcm_s16le", str(tmp)], capture_output=True, text=True)
        if r.returncode == 0 and tmp.exists():
            tmp.replace(wav)
        dur = wav_duration(wav)
        sc["audio"] = str(wav)
        sc["duration"] = round(dur, 2)
        print(f"scene {idx}: {wav.name} — {dur:.2f}s")

    if not args.no_update:
        mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                         encoding="utf-8")
        print(f"manifest updated — real durations in {mpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
