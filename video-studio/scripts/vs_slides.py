#!/usr/bin/env python3
"""vs_slides.py - teacher-style whiteboard slides for educational Reels.

Renders crisp, correct diagrams (no garbled AI text) for video-studio
Reels. 1080x1920 (9:16) whiteboard style: title + sub + typed content.

Usage:
  vs_slides.py spec.json --out-dir images/
  # spec.json = {"slides": [{"kind": "...", "title": "...", "sub": "...",
  #                           "data": {...}}, ...]}

Kinds:
  hook     data: {"badges": ["A","B","C"], "tagline": "..."}
  list     data: {"items": ["1. ...", "2. ..."]}
  grid     data: {"cols": ["R","W","X"], "rows": ["OWNER","GROUP","OTHERS"],
                  "cells": "letters"}
  blocks   data: {"blocks": [{"head":"...","body":"...","color":"blue|green|red"}, ...]}
  summary  data: {"lines": [{"text":"...","color":"..."}, ...], "badge": "..."}
  terminal data: {"title_bar": "bash — user@linux:~", "prompt": "user@linux:~$",
                  "lines": [{"t":"cmd","text":"..."},{"t":"out","text":"..."},
                            {"t":"err","text":"..."}]}  — dark terminal window mock

Exit: 0 ok, 1 on bad spec.
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BLUE, RED, GREEN, DARK = "#1e3a8a", "#b91c1c", "#15803d", "#0f172a"
COLORS = {"blue": BLUE, "green": GREEN, "red": RED, "dark": DARK}


def F(sz, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, sz)


def base(d, title, sub=None):
    img = Image.new("RGB", (W, H), "#f8fafc")
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, W - 40, H - 40], outline="#94a3b8", width=6)
    d.text((W // 2, 150), title, font=F(84), fill=DARK, anchor="mm")
    if sub:
        d.text((W // 2, 250), sub, font=F(42, False), fill=BLUE, anchor="mm")
    d.rectangle([40, H - 90, W - 40, H - 40], fill="#e2e8f0")
    for i, c in enumerate([BLUE, RED, GREEN]):
        d.ellipse([220 + i * 140, H - 75, 260 + i * 140, H - 55], fill=c)
    return img, d


def draw_hook(d, data):
    badges = data.get("badges", [])
    n = len(badges)
    for i, b in enumerate(badges[:4]):
        cx = W // 2 + (i - (n - 1) / 2) * 240
        col = [BLUE, GREEN, RED, DARK][i % 4]
        d.rounded_rectangle([cx - 150, 1000, cx + 150, 1200], radius=24,
                            outline=col, width=8, fill="#ffffff")
        d.text((cx, 1100), b, font=F(54), fill=col, anchor="mm")
    d.text((W // 2, 1450), data.get("tagline", ""), font=F(58),
           fill=DARK, anchor="mm")


def draw_list(d, data):
    y = 500
    for item in data.get("items", [])[:6]:
        d.rounded_rectangle([120, y, W - 120, y + 150], radius=20,
                            outline="#cbd5e1", width=4, fill="#ffffff")
        d.text((W // 2, y + 75), item, font=F(50), fill=DARK, anchor="mm")
        y += 190


def draw_grid(d, data):
    cols = data.get("cols", [])
    rows = data.get("rows", [])
    col_x = [W // 2 + (i - (len(cols) - 1) / 2) * 260 for i in range(len(cols))]
    row_y = [600 + i * 300 for i in range(len(rows))]
    for cx, c in zip(col_x, cols):
        d.text((cx, 420), c, font=F(72), fill=BLUE, anchor="mm")
    for ry, r in zip(row_y, rows):
        d.text((120, ry), r, font=F(52), fill=DARK, anchor="lm")
    for ry in row_y:
        for cx, c in zip(col_x, cols):
            d.rounded_rectangle([cx - 120, ry - 80, cx + 120, ry + 80],
                                radius=18, outline="#cbd5e1", width=4, fill="#ffffff")
            d.text((cx, ry), c, font=F(54), fill=GREEN, anchor="mm")


def draw_blocks(d, data):
    y = 480
    for blk in data.get("blocks", [])[:4]:
        col = COLORS.get(blk.get("color", "blue"), BLUE)
        d.rounded_rectangle([120, y, W - 120, y + 300], radius=26,
                            outline=col, width=10, fill="#ffffff")
        d.text((200, y + 80), blk.get("head", ""), font=F(60), fill=col, anchor="lm")
        d.text((200, y + 200), blk.get("body", ""), font=F(40, False),
               fill=DARK, anchor="lm")
        y += 360


def draw_summary(d, data):
    y = 550
    for line in data.get("lines", [])[:4]:
        col = COLORS.get(line.get("color", "dark"), DARK)
        d.rounded_rectangle([120, y, W - 120, y + 220], radius=24,
                            outline=col, width=8, fill="#ffffff")
        d.text((W // 2, y + 110), line.get("text", ""), font=F(56),
               fill=col, anchor="mm")
        y += 280
    if data.get("badge"):
        d.text((W // 2, 1550), data["badge"], font=F(66), fill=RED, anchor="mm")


MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def draw_terminal(d, data):
    """Dark terminal window mock: title bar, prompt, typed command, output."""
    # window frame (dark)
    x0, y0, x1, y1 = 120, 470, W - 120, 1560
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill="#0f172a",
                        outline="#334155", width=6)
    # title bar
    d.rounded_rectangle([x0, y0, x1, y0 + 90], radius=28, fill="#1e293b")
    d.rectangle([x0, y0 + 45, x1, y0 + 90], fill="#1e293b")
    for i, c in enumerate(["#f87171", "#fbbf24", "#4ade80"]):
        d.ellipse([x0 + 40 + i * 70, y0 + 28, x0 + 76 + i * 70, y0 + 64], fill=c)
    d.text((x0 + 260, y0 + 46), data.get("title_bar", "bash — user@linux:~"),
           font=F(38, False), fill="#94a3b8", anchor="lm")
    # body
    y = y0 + 150
    prompt = data.get("prompt", "user@linux:~$")
    for line in data.get("lines", [])[:9]:
        t = line.get("t", "out")
        text = line.get("text", "")
        if t == "cmd":
            d.text((x0 + 50, y), prompt, font=ImageFont.truetype(MONO, 44),
                   fill="#4ade80", anchor="lm")
            d.text((x0 + 50 + d.textlength(prompt, font=ImageFont.truetype(MONO, 44)) + 20, y),
                   text, font=ImageFont.truetype(MONO, 44), fill="#e2e8f0", anchor="lm")
        elif t == "err":
            d.text((x0 + 50, y), text, font=ImageFont.truetype(MONO, 44),
                   fill="#f87171", anchor="lm")
        else:
            d.text((x0 + 50, y), text, font=ImageFont.truetype(MONO, 44),
                   fill="#cbd5e1", anchor="lm")
        y += 92


KINDS = {"hook": draw_hook, "list": draw_list, "grid": draw_grid,
         "blocks": draw_blocks, "summary": draw_summary,
         "terminal": draw_terminal}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out-dir", default="images")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"not found: {spec_path}", file=sys.stderr)
        return 1
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i, slide in enumerate(spec.get("slides", []), 1):
        kind = slide.get("kind")
        fn = KINDS.get(kind)
        if not fn:
            print(f"bad kind '{kind}' in slide {i}", file=sys.stderr)
            return 1
        img, d = base(None, slide.get("title", ""), slide.get("sub"))
        fn(d, slide.get("data", {}))
        img.save(out / f"scene_{i:02d}.png")
        print(f"scene_{i:02d}.png <- {kind}: {slide.get('title')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
