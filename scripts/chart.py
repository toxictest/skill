#!/usr/bin/env python3
"""Quick chart from a CSV — super-skill data-ai-memory playbook.

Usage:  chart.py data.csv --col value --x label --type bar|line [--out chart.png] [--title T]
Falls back to a text table if matplotlib is unavailable.
"""
import argparse
import csv
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--col", required=True, help="numeric column to plot")
    ap.add_argument("--x", default=None, help="label/x column (default: row index)")
    ap.add_argument("--type", choices=["bar", "line"], default="bar")
    ap.add_argument("--out", default="chart.png")
    ap.add_argument("--title", default=None)
    ap.add_argument("--top", type=int, default=20, help="max rows to plot")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"not found: {p}", file=sys.stderr)
        return 1

    with p.open(newline="", encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("empty csv", file=sys.stderr)
        return 1
    if args.col not in rows[0]:
        print(f"column '{args.col}' not in {list(rows[0])[:12]}", file=sys.stderr)
        return 1

    labels, values = [], []
    for i, r in enumerate(rows[: args.top]):
        lab = (r.get(args.x) or f"#{i}") if args.x else f"#{i}"
        try:
            val = float(str(r[args.col]).replace(",", ""))
        except (ValueError, TypeError):
            continue
        labels.append(str(lab)[:24])
        values.append(val)
    if not values:
        print(f"no numeric values in '{args.col}'", file=sys.stderr)
        return 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"# {args.col} (text fallback — matplotlib missing)\n")
        for lab, val in sorted(zip(labels, values), key=lambda kv: -kv[1]):
            print(f"- {lab}: {val:g}")
        return 0

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=110)
    fig.patch.set_facecolor("#0f1115")
    ax.set_facecolor("#171a21")
    if args.type == "bar":
        ax.bar(labels, values, color="#7c3aed", edgecolor="#22d3ee", linewidth=0.6)
    else:
        ax.plot(labels, values, color="#22d3ee", linewidth=2, marker="o",
                markerfacecolor="#7c3aed")
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.tick_params(colors="#9aa0ae", labelsize=8)
    ax.set_ylabel(args.col, color="#e8eaf0")
    ax.set_title(args.title or f"{args.col} ({args.type})", color="#e8eaf0")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(args.out, facecolor=fig.get_facecolor())
    print(f"wrote {args.out} ({len(values)} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
