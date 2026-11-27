#!/usr/bin/env python3
"""Parse a Markdown video script into a scene manifest (scene timing plan).

Script format (Markdown):
  # Video: <title>
  ## Scene 1 — <shot name>
  | Visual   | <what the camera shows>            |
  | Narration | <what the voiceover says>         |
  | Image    | path/to/img.png  (optional)       |
  | Title    | on-screen text (optional)          |
  | Music    | ambient / uplifting (optional)     |
  | Duration | 4.0  (optional, seconds; default auto) |

Duration "auto" = narration length estimated at ~14 chars/sec (EN/HI TTS
ballpark), clamped to [MIN, MAX]. After vs_tts.py synthesizes narration,
real audio durations overwrite these estimates.

Usage:
  vs_plan.py script.md --out scene_manifest.json [--min 2] [--max 20]
Output: scene_manifest.json {title, width, height, fps, xfade, scenes:[...]}
Exit: 0 ok, 1 on bad input.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SPEED_CPS = 14  # estimated narration characters per second


def parse_script(text: str) -> dict:
    lines = text.splitlines()
    title = "Untitled"
    for ln in lines:
        m = re.match(r"^#\s*Video:\s*(.+)$", ln.strip(), re.I)
        if m:
            title = m.group(1).strip()
            break

    scenes: list[dict] = []
    cur: dict | None = None
    for ln in lines:
        s = ln.strip()
        m = re.match(r"^##\s*Scene\s*(\d+)\s*(?:[—-]\s*(.*))?$", s, re.I)
        if m:
            if cur:
                scenes.append(cur)
            cur = {"index": int(m.group(1)), "name": (m.group(2) or "").strip(),
                   "visual": "", "narration": "", "image": None, "title": None,
                   "music": None, "duration": None}
            continue
        if cur is None:
            continue
        m = re.match(r"^\|\s*([A-Za-z ]+?)\s*\|\s*(.+?)\s*\|\s*$", s)
        if not m:
            continue
        key = m.group(1).strip().lower()
        val = m.group(2).strip()
        if key == "visual":
            cur["visual"] = val
        elif key == "narration":
            cur["narration"] = val
        elif key == "image":
            cur["image"] = val
        elif key == "title":
            cur["title"] = val
        elif key == "music":
            cur["music"] = val
        elif key == "duration":
            try:
                cur["duration"] = float(val)
            except ValueError:
                print(f"warn: bad Duration '{val}' in Scene {cur['index']}, using auto",
                      file=sys.stderr)

    if cur:
        scenes.append(cur)

    if not scenes:
        raise ValueError("no '## Scene N' sections found in script")
    for sc in scenes:
        if not sc["narration"]:
            raise ValueError(f"Scene {sc['index']} has no Narration line")
        if sc["duration"] is None:
            chars = len(re.sub(r"\s+", "", sc["narration"]))
            sc["duration"] = round(max(1.0, chars / SPEED_CPS), 2)
    return {"title": title, "scenes": scenes}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--out", default="scene_manifest.json")
    ap.add_argument("--min", type=float, default=2.0, help="min auto scene duration (s)")
    ap.add_argument("--max", type=float, default=20.0, help="max auto scene duration (s)")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--xfade", type=float, default=0.5,
                    help="crossfade seconds between scenes (0 = hard cut)")
    args = ap.parse_args()

    src = Path(args.script)
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 1
    try:
        plan = parse_script(src.read_text(encoding="utf-8", errors="replace"))
    except ValueError as e:
        print(f"script error: {e}", file=sys.stderr)
        return 1

    for sc in plan["scenes"]:
        sc["duration"] = round(min(max(sc["duration"], args.min), args.max), 2)

    manifest = {
        "title": plan["title"],
        "width": args.width, "height": args.height, "fps": args.fps,
        "xfade": args.xfade,
        "scenes": plan["scenes"],
    }
    out = Path(args.out)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(sc["duration"] for sc in manifest["scenes"]) \
        - args.xfade * max(0, len(manifest["scenes"]) - 1)
    print(f"wrote {out} — {len(manifest['scenes'])} scenes, ~{total:.1f}s total")
    for sc in manifest["scenes"]:
        print(f"  scene {sc['index']}: {sc['duration']:>5}s | {sc['visual'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
