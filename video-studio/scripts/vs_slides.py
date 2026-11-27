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
                            {"t":"err","text":"..."}]}
  Terminal slides ALSO write anim_scene_NN/frame_000.png.. (typewriter
  animation: command types out, output lines appear, blinking cursor).

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
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLUE, RED, GREEN, DARK = "#1e3a8a", "#b91c1c", "#15803d", "#0f172a"
COLORS = {"blue": BLUE, "green": GREEN, "red": RED, "dark": DARK}


def F(sz, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, sz)


def fit_font(text, path, max_size, max_width, bold=True):
    """Shrink font until text fits max_width (min size 18)."""
    sz = max_size
    while sz > 18:
        f = ImageFont.truetype(path, sz)
        if f.getlength(text) <= max_width:
            return f
        sz -= 2
    return ImageFont.truetype(path, 18)


def wrap(text, font, max_width):
    """Greedy word wrap."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


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
        d.rounded_rectangle([cx - 150, 980, cx + 150, 1180], radius=24,
                            outline=col, width=8, fill="#ffffff")
        d.text((cx, 1080), b, font=fit_font(b, BOLD, 46, 280), fill=col, anchor="mm")
    tag = data.get("tagline", "")
    f = fit_font(tag, BOLD, 58, W - 200)
    lines = wrap(tag, f, W - 200)[:2]
    y = 1420 if len(lines) == 1 else 1360
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=DARK, anchor="mm")
        y += 76


def draw_list(d, data):
    items = data.get("items", [])[:6]
    maxw = W - 260  # inner text width
    # measure wrapped lines, pick a font size that fits all items in 2 lines
    size = 50
    wrapped = []
    while size >= 20:
        f = ImageFont.truetype(BOLD, size)
        wrapped = [wrap(it, f, maxw - 60) for it in items]
        if all(len(ln) <= 2 for ln in wrapped):
            break
        size -= 2
    f = ImageFont.truetype(BOLD, size)
    lh = int(size * 1.45)
    y = 480
    for it, lines in zip(items, wrapped):
        box_h = 50 + len(lines) * lh
        d.rounded_rectangle([130, y, W - 130, y + box_h], radius=20,
                            outline="#cbd5e1", width=4, fill="#ffffff")
        ty = y + 50
        for ln in lines:
            d.text((W // 2, ty + lh // 2), ln, font=f, fill=DARK, anchor="mm")
            ty += lh
        y += box_h + 30


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
        head = blk.get("head", "")
        body = blk.get("body", "")
        fh = fit_font(head, BOLD, 60, W - 300)
        fb = fit_font(body, REG, 40, W - 300, bold=False)
        body_lines = wrap(body, fb, W - 300)[:2]
        box_h = 90 + len(body_lines) * 60
        d.rounded_rectangle([120, y, W - 120, y + box_h], radius=26,
                            outline=col, width=10, fill="#ffffff")
        d.text((200, y + 70), head, font=fh, fill=col, anchor="lm")
        ty = y + 160
        for ln in body_lines:
            d.text((200, ty), ln, font=fb, fill=DARK, anchor="lm")
            ty += 60
        y += box_h + 30


def draw_summary(d, data):
    y = 520
    for line in data.get("lines", [])[:4]:
        col = COLORS.get(line.get("color", "dark"), DARK)
        text = line.get("text", "")
        size = 56
        f = fit_font(text, BOLD, size, W - 300)
        lines = wrap(text, f, W - 300)[:2]
        box_h = 40 + len(lines) * int(size * 1.4)
        d.rounded_rectangle([120, y, W - 120, y + box_h], radius=24,
                            outline=col, width=8, fill="#ffffff")
        ty = y + 50
        for ln in lines:
            d.text((W // 2, ty + int(size * 0.7)), ln, font=f, fill=col, anchor="mm")
            ty += int(size * 1.4)
        y += box_h + 24
    if data.get("badge"):
        d.text((W // 2, 1550), data["badge"], font=F(66), fill=RED, anchor="mm")


# ---------------- terminal ----------------

def _term_geom():
    return 120, 470, W - 120, 1560


def _draw_terminal_chrome(d, title_bar):
    x0, y0, x1, y1 = _term_geom()
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill="#0f172a",
                        outline="#334155", width=6)
    d.rounded_rectangle([x0, y0, x1, y0 + 90], radius=28, fill="#1e293b")
    d.rectangle([x0, y0 + 45, x1, y0 + 90], fill="#1e293b")
    for i, c in enumerate(["#f87171", "#fbbf24", "#4ade80"]):
        d.ellipse([x0 + 40 + i * 70, y0 + 28, x0 + 76 + i * 70, y0 + 64], fill=c)
    d.text((x0 + 260, y0 + 46), title_bar, font=F(38, False), fill="#94a3b8", anchor="lm")
    return y0 + 150


def _term_line(d, x, y, text, color, font):
    d.text((x, y), text, font=font, fill=color, anchor="lm")


def _mono_size(lines, max_w=720):
    """Pick a mono font size (<=44) so the longest line fits max_w."""
    sz = 44
    while sz > 20:
        f = ImageFont.truetype(MONO, sz)
        if all(f.getlength(ln.get("text", "")) <= max_w for ln in lines):
            return sz
        sz -= 2
    return 20


def _terminal_body(d, data, chars_shown, cursor_on):
    """Draw terminal body. chars_shown: list of int|None per line (None=hidden)."""
    x0, _, _, _ = _term_geom()
    y = _draw_terminal_chrome(d, data.get("title_bar", "bash — user@linux:~"))
    prompt = data.get("prompt", "user@linux:~$")
    lines = data.get("lines", [])
    msz = _mono_size(lines)
    pf = ImageFont.truetype(MONO, msz)
    tf = ImageFont.truetype(MONO, msz)
    active = None
    for idx, line in enumerate(lines):
        n = chars_shown[idx] if idx < len(chars_shown) else None
        if n is None:
            continue
        t = line.get("t", "out")
        text = line.get("text", "")
        if t == "cmd":
            d.text((x0 + 50, y), prompt, font=pf, fill="#4ade80", anchor="lm")
            d.text((x0 + 50 + pf.getlength(prompt) + 18, y), text[:n],
                   font=tf, fill="#e2e8f0", anchor="lm")
            if n < len(text):
                active = idx
        else:
            col = "#f87171" if t == "err" else "#cbd5e1"
            d.text((x0 + 50, y), text[:n], font=tf, fill=col, anchor="lm")
            if n < len(text):
                active = idx
        if cursor_on and active == idx:
            if t == "cmd":
                cx = x0 + 50 + pf.getlength(prompt) + 18 + tf.getlength(text[:n])
            else:
                cx = x0 + 50 + tf.getlength(text[:n])
            d.rectangle([cx + 4, y - 30, cx + 22, y + 30], fill="#4ade80")
        y += int(msz * 2)
    # cursor on last visible line during hold
    if cursor_on and active is None and lines:
        idx = len(lines) - 1
        line = lines[idx]
        text = line.get("text", "")
        y_cur = _term_geom()[1] + 150 + idx * int(msz * 2)
        if line.get("t") == "cmd":
            cx = x0 + 50 + pf.getlength(prompt) + 18 + tf.getlength(text)
        else:
            cx = x0 + 50 + tf.getlength(text)
        d.rectangle([cx + 4, y_cur - 30, cx + 22, y_cur + 30], fill="#4ade80")


def draw_terminal(d, data):
    chars = [len(ln.get("text", "")) for ln in data.get("lines", [])]
    _terminal_body(d, data, chars, cursor_on=False)


def terminal_frames(data, n=90):
    """Yield PIL Images for a typewriter animation of the terminal slide."""
    lines = data.get("lines", [])
    # build timeline: cmd lines type char-by-char; out lines appear after
    plan = []  # (mode, text, start_frame, per_char)
    t = 0
    for ln in lines:
        text = ln.get("text", "")
        if ln.get("t") == "cmd":
            per = 2
            plan.append(("type", text, t, per))
            t += max(8, 2 * len(text))
        else:
            plan.append(("appear", text, t, 0))
            t += 5
    hold = max(10, n - t)
    for i in range(n):
        chars_shown = []
        for (mode, text, start, per) in plan:
            if i < start:
                chars_shown.append(None)
            elif mode == "type":
                chars_shown.append(min(len(text), max(0, (i - start) // per + 1)))
            else:
                chars_shown.append(len(text))
        cursor_on = (i % 8) < 4
        img, d = base(None, "Terminal Mein Dekho")
        _terminal_body(d, data, chars_shown, cursor_on=cursor_on)
        yield img


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
        if kind == "terminal":
            anim = out / f"anim_scene_{i:02d}"
            anim.mkdir(exist_ok=True)
            n = 0
            for fr in terminal_frames(slide.get("data", {}), n=90):
                fr.save(anim / f"frame_{n:03d}.png")
                n += 1
            print(f"  → anim_scene_{i:02d}/frame_000..{n-1:03d}.png ({n} frames)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
