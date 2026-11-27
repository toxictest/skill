#!/usr/bin/env python3
"""Generate a YouTube SEO kit for a topic: titles, tags, description, chapters.

Usage:
  youtube_seo.py "Linux Basics in Hindi" [--duration 3:56] [--clips clips/]
                 [--out seo.md] [--lang en|hi]
- 5 title options (keyword-first, <=65 chars, numbers/separators)
- tag list (~500 char budget), hashtags, description skeleton
- chapters auto-probed from --clips mp4s (cumulative) with >=10s rule check
Exit: 0 = kit printed/written.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def probe(path: Path) -> float:
    import imageio_ffmpeg
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(path)],
                       capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def title_case_topic(topic: str) -> str:
    return " ".join(w.capitalize() if w.islower() else w for w in topic.split())


def build_titles(topic: str) -> list[str]:
    t = title_case_topic(topic)
    short = t.split("|")[0].split("(")[0].strip()
    return [
        f"{short} | 2026 Complete Guide (Beginner Friendly)",
        f"{short} Kya Hai? Full Tutorial in Hindi (2026)",
        f"{short} — Learn Step by Step in 4 Min",
        f"Complete {short} Course for Beginners | Hindi",
        f"{short} Tutorial 2026 | Everything You Need to Know",
    ]


def build_tags(topic: str) -> str:
    base = [w.lower() for w in re.findall(r"[A-Za-z]+", topic) if len(w) > 2]
    phrase = " ".join(base)
    pool = [
        phrase, f"{phrase} in hindi", f"{phrase} tutorial",
        f"{phrase} for beginners", f"{phrase} kya hai",
        f"learn {phrase}", f"{phrase} 2026", f"{phrase} full course",
        f"{phrase} step by step", "tutorial", "beginner guide",
        "hindi tutorial", "tech hindi", "learn online",
    ]
    seen, tags = set(), []
    for x in pool:
        if x and x not in seen:
            seen.add(x)
            tags.append(x)
    out = ", ".join(tags)
    return out[:497] if len(out) > 500 else out


def build_hashtags(topic: str) -> str:
    words = re.findall(r"[A-Za-z]+", topic)
    tags = ["#" + w.capitalize() for w in words[:3] if len(w) > 2]
    tags += ["#Tutorial", "#LearnOnline"]
    return " ".join(dict.fromkeys(tags))


def build_chapters(clips_dir: Path) -> tuple[str, list[str]]:
    clips = sorted(clips_dir.glob("*.mp4"))
    problems: list[str] = []
    rows, t = [], 0.0
    for c in clips:
        d = probe(c)
        if d <= 0:
            problems.append(f"cannot probe {c.name}")
            continue
        if t > 0 and d < 10:
            problems.append(f"{c.name} is {d:.1f}s < 10s (chapter rule)")
        rows.append((t, c.stem))
        t += d
    lines = [f"{mmss(st)}  {name}" for st, name in rows]
    if rows and rows[0][0] != 0:
        lines.insert(0, "0:00  Intro")
    return "\n".join(lines), problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--duration", default=None, help="e.g. 3:56")
    ap.add_argument("--clips", default=None, help="dir of scene mp4s for chapters")
    ap.add_argument("--out", default=None)
    ap.add_argument("--lang", choices=["en", "hi"], default="hi")
    args = ap.parse_args()

    topic = args.topic
    titles = build_titles(topic)
    tags = build_tags(topic)
    hashtags = build_hashtags(topic)

    chapters, problems = "", []
    if args.clips:
        chapters, problems = build_chapters(Path(args.clips))

    hi_hook = args.lang == "hi"
    hook = (f"{topic} — complete Hindi guide! Sab kuch step by step, "
            f"beginner friendly. Video pasand aaye to LIKE aur SUBSCRIBE karein."
            if hi_hook else
            f"{topic} — complete step-by-step guide for beginners. "
            f"Like & subscribe for more!")

    kit = [f"# YouTube SEO Kit — {topic}", ""]
    if args.duration:
        kit += [f"Duration: {args.duration}", ""]
    kit += ["## Titles (pick 1, keyword-first)", ""]
    kit += [f"{i}. {t}  ({len(t)} chars)" for i, t in enumerate(titles, 1)]
    kit += ["", "## Description (first 2 lines — search visible)", "", hook, "",
            "## Tags (paste in Studio)", "", tags, "",
            "## Hashtags (3 above title)", "", hashtags[:120], ""]
    if chapters:
        kit += ["## Chapters (paste in description)", "", chapters, ""]
        if problems:
            kit += ["> ⚠️ " + p for p in problems]
    else:
        kit += ["## Chapters", "", "_pass --clips <dir> to auto-generate_", ""]
    kit += ["## Checklist",
            "- [ ] Thumbnail 1280x720 (text-safe zone)",
            "- [ ] Subtitle .srt uploaded",
            "- [ ] Category: Education",
            "- [ ] Pinned comment with a question",
            "- [ ] Upload 7-9 PM IST (Tue-Thu/Sun)"]

    text = "\n".join(kit) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(text)} bytes)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
