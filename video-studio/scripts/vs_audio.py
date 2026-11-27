#!/usr/bin/env python3
"""vs_audio.py - normalize narration audio and write real durations into the manifest.

Works with any per-scene audio files (mp3 from native generate_speech, or
any format): converts each to mono 16-bit 44.1k WAV, sets the scene's
"audio" path and "duration" to the real measured seconds.

Usage:
  vs_audio.py scene_manifest.json --audio-dir narration/ [--stem scene_]
Exit: 0 ok, 1 fail.
"""
import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path


def ff() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("missing dependency: imageio-ffmpeg — run: pip install imageio-ffmpeg",
              file=sys.stderr)
        sys.exit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--stem", default="scene_",
                    help="audio file stem pattern (scene_01.*)")
    args = ap.parse_args()

    ffmpeg = ff()
    mpath = Path(args.manifest)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    adir = Path(args.audio_dir)

    for sc in manifest["scenes"]:
        idx = sc["index"]
        src = None
        for ext in (".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac"):
            cand = adir / f"{args.stem}{idx:02d}{ext}"
            if cand.exists():
                src = cand
                break
        if src is None:
            print(f"scene {idx}: no audio file in {adir} matching {args.stem}{idx:02d}.*",
                  file=sys.stderr)
            return 1
        wav = adir / f"{args.stem}{idx:02d}.wav"
        r = subprocess.run([ffmpeg, "-y", "-i", str(src), "-ac", "1", "-ar",
                            "44100", "-c:a", "pcm_s16le", str(wav)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"scene {idx}: convert failed: {r.stderr[-150:]}", file=sys.stderr)
            return 1
        with wave.open(str(wav), "rb") as w:
            dur = w.getnframes() / w.getframerate()
        sc["audio"] = str(wav)
        sc["duration"] = round(dur, 2)
        print(f"scene {idx}: {src.name} -> {dur:.2f}s")

    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                     encoding="utf-8")
    print(f"manifest updated — {len(manifest['scenes'])} scenes with real durations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
