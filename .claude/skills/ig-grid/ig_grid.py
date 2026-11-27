#!/usr/bin/env python3
"""ig_grid.py - plan a cohesive Instagram feed grid or carousel.

    ig_grid.py --idea "sunrise city walk" --idea "rooftop coffee run" \
        --idea "night markets" --layout 3 --out grid_plan.md

Checks thematic cohesion across ideas (keyword overlap) — a grid that reads
as one series gets more saves than a random pile. Assigns grid positions
(snake order for the swipe/scroll journey), flags weak links, and writes
grid_plan.md with per-slot caption hooks.

Layouts: 3 (trigrid), 4 (square), 5, carousel (swipe order matters most).
Exit: 0 ok, 1 on bad input.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def keywords(text: str) -> set[str]:
    stop = {"a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "my",
            "with", "at", "it", "is", "this", "that"}
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3} - stop


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--idea", action="append", required=True,
                    help="one post idea (repeatable)")
    ap.add_argument("--layout", choices=["3", "4", "5", "carousel"], default="3")
    ap.add_argument("--series-name", default=None)
    ap.add_argument("--out", default="grid_plan.md")
    args = ap.parse_args()

    ideas = args.idea[: (5 if args.layout == "carousel" else int(args.layout))]
    if len(ideas) < 2:
        print("need >= 2 --idea values", file=sys.stderr)
        return 1

    wordsets = [keywords(i) for i in ideas]
    all_words = Counter()
    for ws in wordsets:
        all_words.update(ws)
    series_kw = {w for w, _ in all_words.most_common(4)}

    # cohesion: share of ideas touching the series keywords
    coherence = sum(1 for ws in wordsets if ws & series_kw) / len(ideas)

    # snake order: for grids, position flow 1->2->3 / 6->5->4 (zigzag)
    order = list(range(len(ideas)))
    if args.layout != "carousel":
        per_row = int(args.layout)
        snake = []
        for r in range(0, len(ideas), per_row):
            row = order[r:r + per_row]
            snake += row if (r // per_row) % 2 == 0 else row[::-1]
        order = snake

    weak = [ideas[i] for i in range(len(ideas))
            if not (wordsets[i] & series_kw) and len(ideas) > 3]

    lines = [f"# Instagram grid plan — {args.series_name or 'series'}",
             f"layout: {args.layout} · ideas: {len(ideas)} · "
             f"cohesion: {coherence:.0%}", ""]
    if coherence >= 0.6:
        lines.append(f"✅ theme holds across the set (series keywords: "
                     f"{', '.join(sorted(series_kw))})")
    else:
        lines.append(f"⚠️ theme is loose — center the grid on "
                     f"{', '.join(sorted(series_kw))} or split into two series")
    if weak:
        lines.append(f"⚠️ weakest links (off-theme): " + "; ".join(weak))
    lines += ["", "## Slot order", ""]
    for pos, idx in enumerate(order, 1):
        kw = ", ".join(sorted(wordsets[idx])) or "—"
        lines.append(f"**slot {pos}** — {ideas[idx]}  \n"
                     f"keywords: {kw} · hook: lead with the strongest "
                     f"visual noun, ≤ 125 chars")
    lines += ["", "## Rules",
              "- cover text stays inside safe zones (see ig-reels)",
              "- one series name + consistent cover style across slots",
              "- alt text on every post (accessibility + reach)",
              "- carousel: slide 1 = the hook frame, last slide = CTA/save"]
    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
