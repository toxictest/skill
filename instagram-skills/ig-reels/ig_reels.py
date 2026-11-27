#!/usr/bin/env python3
"""ig_reels.py - validate a Reel against IG specs and make a safe-zone cover.

    ig_reels.py --video reel.mp4 [--title "Hook text"] [--out cover.jpg]
      [--at 1.0]            # cover frame time (default: 10% in, capped 3s)
      [--max-seconds 90]    # duration ceiling (IG allows longer; 90s is safe)

Checks: 9:16 aspect (1080x1920 target), duration, decode integrity, audio
presence. Draws IG UI safe zones on the cover (top 14% / bottom 25% /
right 20% must stay clear of text) and writes reels_plan.md.
Exit: 0 ok, 1 fail (with reasons).
"""
import argparse
import re
import subprocess
import sys
import tempfile
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
    ap.add_argument("--video", required=True)
    ap.add_argument("--title", default=None)
    ap.add_argument("--out", default="cover.jpg")
    ap.add_argument("--at", type=float, default=None)
    ap.add_argument("--max-seconds", type=float, default=90.0)
    args = ap.parse_args()

    ffmpeg = ff()
    v = Path(args.video)
    if not v.exists():
        print(f"not found: {v}", file=sys.stderr)
        return 1

    pr = subprocess.run([ffmpeg, "-i", str(v)], capture_output=True, text=True)
    err = pr.stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    dur = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3)) if m else 0
    m = re.search(r"Video: \w+.*? (\d+)x(\d+)", err, re.DOTALL)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    has_audio = "Audio:" in err

    problems = []
    if w and h:
        ratio = w / h
        if not 0.45 <= ratio <= 0.56:  # 9:16 ≈ 0.5625, allow slight crop
            problems.append(f"aspect {w}x{h} ({ratio:.2f}) — Reels want 9:16 "
                            f"(1080x1920); re-render with video-studio "
                            f"--width 1080 --height 1920")
    if dur > args.max_seconds:
        problems.append(f"duration {dur:.0f}s > {args.max_seconds:.0f}s ceiling")
    if not has_audio:
        problems.append("no audio track (Reels with sound perform better)")

    dec = subprocess.run([ffmpeg, "-v", "error", "-i", str(v), "-f", "null", "-"],
                         capture_output=True, text=True)
    if dec.returncode != 0 or dec.stderr.strip():
        problems.append("decode errors — fix the source before publishing")

    at = args.at if args.at is not None else min(3.0, dur * 0.1 if dur else 1.0)
    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / "f.jpg"
        r = subprocess.run([ffmpeg, "-y", "-ss", f"{at:.2f}", "-i", str(v),
                            "-frames:v", "1", "-q:v", "2", str(frame)],
                           capture_output=True, text=True)
        if r.returncode == 0 and frame.exists():
            try:
                from PIL import Image, ImageDraw, ImageFont
            except ImportError:
                print("missing dependency: pillow — run: pip install pillow",
                      file=sys.stderr)
                return 1
            W, H = 1080, 1920
            img = Image.open(frame).convert("RGB").resize((W, H), Image.LANCZOS)
            dr = ImageDraw.Draw(img)
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if not Path(font_path).exists():
                try:
                    import matplotlib
                    font_path = str(Path(matplotlib.__file__).parent /
                                   "mpl-data/fonts/ttf/DejaVuSans-Bold.ttf")
                except ImportError:
                    font_path = None
            font = ImageFont.truetype(font_path, 64) if font_path else None
            # safe zones: top 14%, bottom 25%, right 20%
            dr.rectangle([0, 0, W, int(H * 0.14)], outline=(255, 0, 0), width=6)
            dr.rectangle([0, int(H * 0.75), W, H], outline=(255, 0, 0), width=6)
            dr.rectangle([int(W * 0.80), 0, W, int(H * 0.75)],
                         outline=(255, 0, 0), width=6)
            if args.title and font:
                dr.text((W // 2, H * 0.45), args.title[:40], fill=(255, 255, 255),
                        font=font, anchor="mm")
            dr.text((W // 2, int(H * 0.14) - 40), "KEEP CLEAR (UI)",
                    fill=(255, 0, 0), font=font, anchor="mm")
            out = Path(args.out)
            img.save(out, quality=88)
            print(f"wrote {out} ({out.stat().st_size // 1024} KB, cover @ {at:.1f}s)")
        else:
            print("cover frame grab failed", file=sys.stderr)
            problems.append("cover frame grab failed")

    plan = f"""# Reels plan — {v.name}

- specs: {w}x{h}, {dur:.1f}s, audio: {has_audio}
- verdict: **{'PASS' if not problems else 'ISSUES'}**
"""
    if problems:
        plan += "\n".join(f"- ⚠️ {p}" for p in problems) + "\n"
    else:
        plan += "\n- all checks passed — safe to publish\n"
    plan += (
        "\n## Before posting\n"
        "- keep text inside the safe zones visible on the cover\n"
        "- caption: lead with a hook ≤ 125 chars, then the body, 5–15 hashtags\n"
        "- first frame / cover: use the red-marked frame as the cover\n"
        "- post when the audience is awake; reply to comments in the first hour\n")
    (Path(args.out).with_suffix(".plan.md")).write_text(plan, encoding="utf-8")
    print(plan)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
