#!/usr/bin/env python3
"""Generate/verify MANIFEST.json — sha256 inventory for supply-chain integrity.

Usage:
  python3 scripts/make_manifest.py            # write MANIFEST.json
  python3 scripts/make_manifest.py --verify   # check files against manifest
Exit: 0 ok, 1 mismatch/missing (tamper or partial copy detected).
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "MANIFEST.json"
SKIP = {"MANIFEST.json", "super-skill.zip"}


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory() -> dict:
    files = {}
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.name in SKIP or "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        files[rel] = {"sha256": digest(p), "size": p.stat().st_size}
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if not args.verify:
        files = inventory()
        data = {
            "name": "super-skill",
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "file_count": len(files),
            "total_bytes": sum(f["size"] for f in files.values()),
            "files": files,
        }
        MANIFEST.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"MANIFEST.json written — {data['file_count']} files, "
              f"{data['total_bytes'] // 1024} KB total")
        return 0

    if not MANIFEST.exists():
        print("MANIFEST.json missing — run make_manifest.py first", file=sys.stderr)
        return 1
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected: dict = data["files"]
    actual = inventory()
    problems = []
    for rel, meta in expected.items():
        if rel not in actual:
            problems.append(f"MISSING  {rel}")
        elif actual[rel]["sha256"] != meta["sha256"]:
            problems.append(f"CHANGED  {rel}")
    for rel in actual:
        if rel not in expected:
            problems.append(f"EXTRA    {rel}")
    if problems:
        print(f"INTEGRITY FAIL — {len(problems)} problem(s):")
        for p in problems[:30]:
            print(" ", p)
        return 1
    print(f"INTEGRITY OK — {len(expected)} files match MANIFEST.json ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
