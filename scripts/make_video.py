#!/usr/bin/env python3
"""Make an MP4 from images (+ optional narration) — super-skill creative-media video pipeline.

Usage:
  make_video.py frame1.png frame2.png ... --out video.mp4
  make_video.py slides/*.png --duration 2.5 --fps 24 --audio narration.mp3 --out demo.mp4
  make_video.py --demo --out demo.mp4          # generated gradient frames (self-test)

Deps: pillow, imageio, imageio-ffmpeg (pip install pillow imageio imageio-ffmpeg)
Exit: 0 = written, prints path + size. Audio is muxed via bundled ffmpeg.
"""
import argparse
import glob
import subprocess
import sys
from pathlib import Path


def demo_frames(size: tuple[int, int], n: int = 6) -> list:
    from PIL import Image, ImageDraw
    frames = []
    w, h = size
    for i in range(n):
        img = Image.new("RGB", size)
        d = ImageDraw.Draw(img)
        # brand gradient sweep
        for x in range(0, w, 4):
            t = x / w
            r = int(124 + (34 - 124) * t)
            g = int(58 + (211 - 58) * t)
            b = int(237 + (238 - 237) * t)
            # vary by frame index
            r = (r + i * 18) % 256
            d.rectangle([x, 0, x + 4, h], fill=(r, g, b))
        d.ellipse([w * 0.35, h * 0.3, w * 0.65, h * 0.7], fill=(15, 17, 21))
        frames.append(img)
    return frames


def load_frames(paths: list[Path], size: tuple[int, int]) -> list:
    from PIL import Image
    frames = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        frames.append(img)
    return frames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="*", help="image files (png/jpg) or globs")
    ap.add_argument("--out", default="video.mp4")
    ap.add_argument("--duration", type=float, default=2.0, help="seconds per image")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", default="1280x720", help="WxH")
    ap.add_argument("--audio", default=None, help="narration audio to mux in")
    ap.add_argument("--demo", action="store_true", help="self-test with generated frames")
    args = ap.parse_args()

    w, h = (int(v) for v in args.size.lower().split("x"))
    size = (w, h)

    if args.demo:
        frames = demo_frames(size)
    else:
        paths: list[Path] = []
        for pat in args.images:
            matched = sorted(glob.glob(pat))
            paths += [Path(m) for m in matched] if matched else [Path(pat)]
        paths = [p for p in paths if p.exists()]
        if not paths:
            print("no images found — pass image paths or --demo", file=sys.stderr)
            return 1
        try:
            frames = load_frames(paths, size)
        except Exception as exc:  # noqa: BLE001
            print(f"image load failed: {exc}", file=sys.stderr)
            return 1

    try:
        import imageio_ffmpeg  # noqa: F401  (availability check)
    except ImportError:
        print("imageio-ffmpeg missing — pip install imageio imageio-ffmpeg", file=sys.stderr)
        return 1

    out = Path(args.out)
    if out.suffix.lower() != ".mp4":
        out = out.with_suffix(".mp4")

    repeat = max(1, int(args.duration * args.fps))
    n_written = 0
    with _FFMPEGWriter(str(out), args.fps, size) as writer:
        for fr in frames:
            for _ in range(repeat):
                writer.append(fr)
                n_written += 1

    print(f"video frames: {n_written} ({len(frames)} images × {repeat} @ {args.fps}fps)")

    if args.audio:
        audio = Path(args.audio)
        if not audio.exists():
            print(f"audio not found: {audio} — video saved without narration", file=sys.stderr)
        else:
            import imageio_ffmpeg
            tmp = out.with_name(out.stem + "_noaudio.mp4")
            out.rename(tmp)
            cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-i", str(tmp),
                   "-i", str(audio), "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                tmp.unlink()
                print("narration muxed ✅")
            else:
                tmp.replace(out)
                print(f"audio mux failed (kept silent video): {r.stderr.strip()[-200:]}",
                      file=sys.stderr)

    if not out.exists() or out.stat().st_size == 0:
        print("FAILED — empty output", file=sys.stderr)
        return 1
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


def _has_pyav() -> bool:
    try:
        import pyav  # noqa: F401
        return True
    except ImportError:
        return False


class _FFMPEGWriter:
    """Fallback: pipe raw frames to the bundled ffmpeg binary."""
    def __init__(self, path: str, fps: int, size: tuple[int, int]):
        import imageio_ffmpeg
        self.proc = subprocess.Popen(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo",
             "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
             "-r", str(fps), "-i", "-", "-pix_fmt", "yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", path],
            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.size = size

    def append(self, frame) -> None:
        self.proc.stdin.write(frame.tobytes())

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.proc.stdin.close()
        self.proc.wait()


def _fallback_writer(path: Path, fps: int):
    return _FFMPEGWriter(str(path), fps, _FALLBACK_SIZE)


_FALLBACK_SIZE = (1280, 720)


if __name__ == "__main__":
    # keep size in scope for fallback writer
    _ap = argparse.ArgumentParser(add_help=False)
    _ap.add_argument("--size", default="1280x720")
    _known, _ = _ap.parse_known_args()
    try:
        _FALLBACK_SIZE = tuple(int(v) for v in _known.size.lower().split("x"))  # type: ignore[assignment]
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main())
