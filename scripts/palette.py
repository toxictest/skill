#!/usr/bin/env python3
"""Generate a color palette from a base hex — super-skill creative-media playbook.

Usage:  palette.py #7c3aed [--svg out.svg] [--count 5]
Output: shades/tints table with WCAG contrast vs black & white + optional SVG swatches.
"""
import argparse
import sys
from pathlib import Path


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"invalid hex: {h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(v))) for v in (r, g, b)))


def rel_luminance(r: int, g: int, b: int) -> float:
    def ch(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(rgb1, rgb2) -> float:
    l1, l2 = sorted((rel_luminance(*rgb1), rel_luminance(*rgb2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def shift(rgb, factor: float) -> tuple[int, int, int]:
    # factor <1 = darker shade, >1 = lighter tint
    return tuple(int(c * factor) for c in rgb)  # type: ignore[return-value]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="base hex color, e.g. #7c3aed")
    ap.add_argument("--count", type=int, default=4, help="shades each side")
    ap.add_argument("--svg", default=None, help="write swatches SVG to this path")
    args = ap.parse_args()

    try:
        base = hex_to_rgb(args.base)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    steps = [i / (args.count + 1) for i in range(1, args.count + 1)]
    colors: list[tuple[str, str]] = []
    for f in reversed(steps):  # dark → light on one side
        c = shift(base, f)
        colors.append((rgb_to_hex(*c), "shade"))
    colors.append((rgb_to_hex(*base), "base"))
    for f in steps:  # tints
        c = tuple(int(v + (255 - v) * f) for v in base)
        colors.append((rgb_to_hex(*c), "tint"))

    print(f"# Palette from {args.base}\n")
    print("| Hex | Role | vs Black | vs White | Sample |")
    print("|---|---|---|---|---|")
    black, white = (0, 0, 0), (255, 255, 255)
    rows = []
    for hx, role in colors:
        rgb = hex_to_rgb(hx)
        cb, cw = contrast(rgb, black), contrast(rgb, white)
        rows.append((hx, role, rgb))
        print(f"| {hx} | {role} | {cb:.1f}:1 | {cw:.1f}:1 | ⬛⬜ |")
    print("\nWCAG: text needs ≥4.5:1 (AA), ≥7:1 (AAA). Use the stronger side for text.")

    if args.svg:
        w = len(rows) * 120
        sw = "".join(
            f'<rect x="{i*120}" y="0" width="120" height="90" fill="{hx}"/>'
            f'<text x="{i*120+60}" y="112" text-anchor="middle" font-family="monospace" '
            f'font-size="13" fill="#e8eaf0">{hx}</text>'
            for i, (hx, _, _) in enumerate(rows))
        Path(args.svg).write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="130" '
            f'viewBox="0 0 {w} 130"><rect width="{w}" height="130" fill="#0f1115"/>{sw}</svg>',
            encoding="utf-8")
        print(f"\nwrote {args.svg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
