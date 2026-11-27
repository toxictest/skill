#!/usr/bin/env python3
"""Profile a CSV/XLSX dataset before analysis — super-skill data-ai-memory playbook.

Usage:  csv_profile.py FILE [--head N]
Output: markdown report — shape, duplicates, nulls, per-column stats, head.
"""
import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Profile a CSV/XLSX file")
    ap.add_argument("file", help=".csv or .xlsx path")
    ap.add_argument("--head", type=int, default=5, help="rows to preview (default 5)")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"not found: {p}", file=sys.stderr)
        return 1

    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed — run: pip install pandas openpyxl", file=sys.stderr)
        return 1

    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p)
    elif p.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(p)
    else:
        print(f"unsupported: {p.suffix} (use .csv or .xlsx)", file=sys.stderr)
        return 1

    print(f"# Profile: {p.name}")
    print(f"- rows = {len(df)}, columns = {len(df.columns)}")
    print(f"- duplicate rows: {int(df.duplicated().sum())}")
    fully_null = [c for c in df.columns if df[c].isna().all()]
    print(f"- fully-null columns: {fully_null or 'none'}")
    num = df.select_dtypes("number")
    if not num.empty:
        print(f"- numeric columns: {list(num.columns)}")

    print("\n| column | dtype | nulls | unique | sample |")
    print("|---|---|---|---|---|")
    for c in df.columns:
        s = df[c]
        sample = ", ".join(str(v) for v in s.dropna().unique()[:3])
        if len(sample) > 55:
            sample = sample[:55] + "…"
        print(f"| {c} | {s.dtype} | {int(s.isna().sum())} | {s.nunique()} | {sample} |")

    print(f"\n## head({args.head})\n")
    print(df.head(args.head).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
