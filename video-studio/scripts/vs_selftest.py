#!/usr/bin/env python3
"""Hermetic end-to-end test of the video-studio pipeline — run before shipping.

Builds a 2-scene demo: plan → silent TTS → render → QC → thumbnail, and
verifies every output. No network, no API keys (silent engine only).

Usage:  python3 scripts/vs_selftest.py [--keep]
Exit: 0 = pipeline healthy, 1 = failure.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def sh(cmd: list[str], cwd: Path | None = None, timeout: int = 180):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, check=False)


SCRIPT = """# Video: Self-Test Sunrise

## Scene 1 — Hook
| Visual    | Cinematic sunrise over a calm city skyline, warm light |
| Narration | Welcome to the studio self test. |
| Title     | Self-Test |

## Scene 2 — Outro
| Visual    | Soft focus rooftops in morning haze |
| Narration | That is the pipeline, end to end. |
| Title     | Done |
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="keep the demo folder")
    args = ap.parse_args()

    print("video-studio self-test\n" + "=" * 46)
    td = Path(tempfile.mkdtemp(prefix="vs_selftest_"))
    script = td / "script.md"
    script.write_text(SCRIPT, encoding="utf-8")
    imgs = td / "images"
    imgs.mkdir()
    try:
        # 1) plan
        r = sh([sys.executable, str(HERE / "vs_plan.py"), str(script),
                "--out", str(td / "scene_manifest.json"), "--min", "1.5", "--max", "6"])
        record("vs_plan parses script", r.returncode == 0
               and (td / "scene_manifest.json").exists())
        manifest = json.loads((td / "scene_manifest.json").read_text())
        record("vs_plan timings sane",
               all(1.5 <= sc["duration"] <= 6 for sc in manifest["scenes"]))

        # 2) silent TTS (hermetic)
        r = sh([sys.executable, str(HERE / "vs_tts.py"), str(td / "scene_manifest.json"),
                "--out-audio", str(td / "narration"), "--engine", "silent"])
        manifest = json.loads((td / "scene_manifest.json").read_text())
        record("vs_tts silent + durations", r.returncode == 0
               and all(sc.get("audio") and sc.get("duration") for sc in manifest["scenes"]))

        # 3) render (placeholder art, xfade)
        r = sh([sys.executable, str(HERE / "vs_render.py"), str(td / "scene_manifest.json"),
                "--out", str(td / "video.mp4"), "--work", str(td / "work"),
                "--xfade", "0.4"], timeout=300)
        video = td / "video.mp4"
        record("vs_render real MP4", r.returncode == 0 and video.exists()
               and video.stat().st_size > 10_000, r.stderr[-120:])

        # 4) QC gate
        r = sh([sys.executable, str(HERE / "vs_qc.py"), str(video),
                "--out", str(td / "QC.md")], timeout=120)
        qc_txt = (td / "QC.md").read_text() if (td / "QC.md").exists() else ""
        record("vs_qc report", r.returncode in (0, 1) and "decode" in qc_txt)

        # 5) thumbnail
        r = sh([sys.executable, str(HERE / "vs_thumb.py"), str(video),
                "--title", "Self-Test Sunrise", "--out", str(td / "thumb.jpg")],
               timeout=120)
        thumb = td / "thumb.jpg"
        record("vs_thumb jpg", r.returncode == 0 and thumb.exists()
               and thumb.stat().st_size > 1000)
    finally:
        if args.keep:
            print(f"\ndemo kept at: {td}")
        else:
            import shutil
            shutil.rmtree(td, ignore_errors=True)

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(f"{'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail and not ok else ""))
    print("=" * 46)
    print(f"{npass}/{len(results)} passed — "
          + ("VIDEO-STUDIO HEALTHY ✅" if npass == len(results) else "FAILURES ❌"))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
