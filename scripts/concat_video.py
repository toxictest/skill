#!/usr/bin/env python3
"""Concatenate MP4 clips into one video (bundled static ffmpeg — no system install).

Usage:
  concat_video.py a.mp4 b.mp4 c.mp4 --out final.mp4
  concat_video.py --glob 'clips/*.mp4' --out final.mp4
  concat_video.py a.mp4 b.mp4 --reencode --out final.mp4   # force re-encode
Strategy: probe every clip first; if all share codec/size/fps, use the
concat demuxer + stream copy (instant); otherwise (or on --reencode)
re-encode with libx264/AAC. Adds +faststart for web/YouTube.
Exit: 0 = written (prints duration + size), 1 = fail.
"""
import argparse
import glob
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def ff() -> str:
    try:
        import imageio_ffmpeg
    except ImportError:
        print("missing dependency: imageio-ffmpeg — run: pip install imageio-ffmpeg",
              file=sys.stderr)
        sys.exit(1)
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: Path) -> dict:
    """Return duration + stream info (codec, width, height, fps) or {} if unreadable."""
    r = subprocess.run([ff(), "-i", str(path)], capture_output=True, text=True)
    err = r.stderr
    info: dict = {}
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    if m:
        info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.search(r"Stream #\d+:\d+.*?Video: (\w+).*?, (\d+)x(\d+).*?(?:, (\d+(?:\.\d+)?) fps|, (\d+(?:\.\d+)?) fps)?",
                  err, re.DOTALL)
    if m:
        info["codec"] = m.group(1)
        info["width"] = int(m.group(2))
        info["height"] = int(m.group(3))
        fps = m.group(4) or m.group(5)
        info["fps"] = float(fps) if fps else None
    m = re.search(r"Stream #\d+:\d+.*?Audio: (\w+)", err, re.DOTALL)
    if m:
        info["audio_codec"] = m.group(1)
    return info


def compatible(infos: list[dict]) -> bool:
    """Stream-copy needs identical video codec/size/fps (audio optional)."""
    vs = [i for i in infos if i.get("codec")]
    if not vs:
        return False
    ref = vs[0]
    for i in vs[1:]:
        if (i.get("codec") != ref.get("codec")
                or i.get("width") != ref.get("width")
                or i.get("height") != ref.get("height")
                or i.get("fps") != ref.get("fps")):
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--glob", default=None, help="glob pattern instead of args")
    ap.add_argument("--out", default="final.mp4")
    ap.add_argument("--reencode", action="store_true",
                    help="force re-encode (skip stream copy even if compatible)")
    args = ap.parse_args()

    clips = [Path(c) for c in args.clips]
    if args.glob:
        clips += [Path(p) for p in sorted(glob.glob(args.glob))]
    clips = [c for c in clips if c.exists()]
    if len(clips) < 2:
        print(f"need >=2 clips, got {len(clips)}", file=sys.stderr)
        return 1

    ffmpeg = ff()
    infos = [probe(c) for c in clips]
    for c, i in zip(clips, infos):
        if not i:
            print(f"cannot read clip: {c}", file=sys.stderr)
            return 1

    copy_ok = compatible(infos)
    mode = "stream-copy"
    if args.reencode or not copy_ok:
        if args.reencode:
            print("--reencode: re-encoding all clips", file=sys.stderr)
        else:
            ref = infos[0]
            print(f"clips differ (e.g. {ref.get('codec')} {ref.get('width')}x"
                  f"{ref.get('height')}) — re-encoding to normalize", file=sys.stderr)
        mode = "re-encode"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        for c in clips:
            fh.write(f"file '{c.resolve()}'\n")
        listfile = fh.name

    out = Path(args.out)
    if mode == "stream-copy":
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
               "-c", "copy", "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("stream-copy failed → falling back to re-encode...", file=sys.stderr)
            mode = "re-encode"
    if mode == "re-encode":
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
               "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
               "-c:a", "aac", "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
    Path(listfile).unlink(missing_ok=True)
    if r.returncode != 0 or not out.exists():
        print((r.stdout + r.stderr)[-400:], file=sys.stderr)
        return 1

    dur = probe(out).get("duration", -1.0)
    # full decode sanity check
    dec = subprocess.run([ffmpeg, "-v", "error", "-i", str(out), "-f", "null", "-"],
                         capture_output=True, text=True)
    ok = dec.returncode == 0 and not dec.stderr.strip()
    print(f"wrote {out} — {int(dur // 60)}:{int(dur % 60):02d}, "
          f"{out.stat().st_size // 1024} KB, {len(clips)} clips [{mode}], "
          f"decode {'clean ✅' if ok else 'ERRORS ❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
