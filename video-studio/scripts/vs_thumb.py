#!/usr/bin/env python3
"""Make a YouTube-style thumbnail (1280x720) from a video + title text.

Usage:
  vs_thumb.py video.mp4 --title "Your Title Here" --out thumb.jpg
      [--at 1.5]            # grab frame at t seconds (default: 10% in)
      [--subtitle "optional sub text"]
Writes 1280x720 JPEG with title card at bottom (dark scrim + bold text).
Exit: 0 ok, 1 fail.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def ff() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("missing dependency: imageio-ffmpeg — run: pip install imageio-ffmpeg",
              file=sys.stderr)
        sys.exit(1)


def find_font() -> str | None:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    try:
        import matplotlib
        p = Path(matplotlib.__file__).parent / "mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"
        if p.exists():
            return str(p)
    except ImportError:
        pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--at", type=float, default=None, help="frame time in seconds")
    ap.add_argument("--out", default="thumb.jpg")
    args = ap.parse_args()

    ffmpeg = ff()
    v = Path(args.video)
    if not v.exists():
        print(f"not found: {v}", file=sys.stderr)
        return 1
    # duration for default grab point
    pr = subprocess.run([ffmpeg, "-i", str(v)], capture_output=True, text=True)
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", pr.stderr)
    dur = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3)) if m else 3.0
    at = args.at if args.at is not None else min(1.5, dur * 0.1)

    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / "frame.jpg"
        r = subprocess.run([ffmpeg, "-y", "-ss", f"{at:.2f}", "-i", str(v),
                            "-frames:v", "1", "-q:v", "2", str(frame)],
                           capture_output=True, text=True)
        if r.returncode != 0 or not frame.exists():
            print(f"frame grab failed:\n{(r.stdout + r.stderr)[-300:]}", file=sys.stderr)
            return 1
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("missing dependency: pillow — run: pip install pillow",
                  file=sys.stderr)
            return 1
        W, H = 1280, 720
        img = Image.open(frame).convert("RGB")
        img = img.resize((W, H), Image.LANCZOS)
        draw = ImageDraw.Draw(img)
        font_path = find_font()
        big = ImageFont.truetype(font_path, 58) if font_path else ImageFont.load_default()
        small = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
        # bottom scrim
        scrim = Image.new("RGBA", (W, 230), (0, 0, 0, 0))
        sd = ImageDraw.Draw(scrim)
        for y in range(230):
            sd.line([(0, y), (W, y)],
                    fill=(0, 0, 0, int(200 * max(0.0, 1 - y / 230 * 0.35))))
        img = img.convert("RGBA")
        img.paste(scrim, (0, H - 230), scrim)
        draw = ImageDraw.Draw(img)
        # wrap title
        def wrap(text, font, max_w):
            words, lines, cur = text.split(), [], ""
            for wd in words:
                trial = (cur + " " + wd).strip()
                if draw.textlength(trial, font=font) <= max_w:
                    cur = trial
                else:
                    if cur:
                        lines.append(cur)
                    cur = wd
            if cur:
                lines.append(cur)
            return lines
        y = H - 230 + 30
        for ln in wrap(args.title, big, W - 80)[:2]:
            tw = draw.textlength(ln, font=big)
            draw.text(((W - tw) / 2, y), ln, font=big, fill=(255, 255, 255))
            y += 72
        if args.subtitle:
            sw = draw.textlength(args.subtitle, font=small)
            draw.text(((W - sw) / 2, y + 6), args.subtitle, font=small,
                      fill=(180, 200, 255))
        out = Path(args.out)
        img.convert("RGB").save(out, quality=88)
        print(f"wrote {out} — {out.stat().st_size // 1024} KB (frame @ {at:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
