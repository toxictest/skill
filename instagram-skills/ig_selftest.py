#!/usr/bin/env python3
"""Hermetic end-to-end test of the instagram-skills pack.

Builds a tiny 9:16 test reel with ffmpeg, then runs ig_caption, ig_reels
and ig_grid and verifies outputs. No network, no API keys.

Usage:  python3 ig_selftest.py
Exit: 0 = pack healthy, 1 = failure.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def sh(cmd: list[str], cwd: Path | None = None, timeout: int = 120):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, check=False)


def main() -> int:
    print("instagram-skills self-test\n" + "=" * 42)
    td = Path(tempfile.mkdtemp(prefix="ig_selftest_"))
    try:
        # 1) ig_caption
        r = sh([sys.executable, str(HERE / "ig-caption" / "ig_caption.py"),
                "--topic", "sunrise city walk", "--audience", "travel lovers",
                "--variants", "3", "--out", str(td / "caption.md")])
        cap = (td / "caption.md").read_text() if (td / "caption.md").exists() else ""
        record("ig_caption generates + lints", r.returncode == 0
               and "Variant" in cap and "hashtags" in cap, r.stderr[-100:])

        # 2) make a test reel (9:16, 3s, audio)
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        reel = td / "reel.mp4"
        sh([ff, "-y", "-f", "lavfi", "-i", "color=c=0x1a1a2e:s=1080x1920:d=3",
            "-f", "lavfi", "-i", "sine=frequency=220:duration=3",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-t", "3", str(reel)], timeout=120)

        r = sh([sys.executable, str(HERE / "ig-reels" / "ig_reels.py"),
                "--video", str(reel), "--title", "Sunrise Test",
                "--out", str(td / "cover.jpg")], timeout=120)
        plan = (td / "cover.plan.md").read_text() if (td / "cover.plan.md").exists() else ""
        cover_ok = (td / "cover.jpg").exists() and (td / "cover.jpg").stat().st_size > 1000
        record("ig_reels validates + cover", r.returncode == 0 and cover_ok
               and "PASS" in plan, r.stderr[-100:])

        # 3) ig_grid
        r = sh([sys.executable, str(HERE / "ig-grid" / "ig_grid.py"),
                "--idea", "sunrise city walk", "--idea", "rooftop coffee run",
                "--idea", "night market lights", "--layout", "3",
                "--series-name", "City Mornings",
                "--out", str(td / "grid_plan.md")])
        grid = (td / "grid_plan.md").read_text() if (td / "grid_plan.md").exists() else ""
        record("ig_grid plans + coherence", r.returncode == 0
               and "slot" in grid and "cohesion" in grid, r.stderr[-100:])
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(f"{'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail and not ok else ""))
    print("=" * 42)
    print(f"{npass}/{len(results)} passed — "
          + ("INSTAGRAM PACK HEALTHY ✅" if npass == len(results) else "FAILURES ❌"))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
