#!/usr/bin/env python3
"""Detect a project and run its standard checks — super-skill coding-dev playbook.

Usage:  run_checks.py [DIR] [--only lint,test,build] [--list]
Runs first match per category found in DIR (default .), prints command + result.
Dry-run with --list. Never runs unknown custom commands.
"""
import argparse
import subprocess
import sys
from pathlib import Path

# category -> [(detector files, command args)]
CHECKS: dict[str, list[tuple[list[str], list[str]]]] = {
    "lint": [
        ([".eslintrc", ".eslintrc.js", ".eslintrc.json", "eslint.config.js"], ["npx", "--yes", "eslint", "."]),
        (["ruff.toml", ".ruff.toml"], ["ruff", "check", "."]),
        (["setup.py", "pyproject.toml", "requirements.txt"], ["python3", "-m", "py_compile"]),
    ],
    "test": [
        (["pytest.ini"], ["python3", "-m", "pytest", "-q"]),
        (["package.json"], ["npm", "test", "--silent"]),
        (["Makefile"], ["make", "test"]),
    ],
    "build": [
        (["package.json"], ["npm", "run", "build", "--silent"]),
        (["Makefile"], ["make", "build"]),
        (["pyproject.toml", "setup.py"], ["python3", "-m", "build", "--no-isolation"]),
    ],
}


def detect(root: Path, candidates: list[str]) -> bool:
    return any((root / f).exists() for f in candidates)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default=".")
    ap.add_argument("--only", default="lint,test,build", help="comma categories")
    ap.add_argument("--list", action="store_true", help="dry-run: print commands only")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    root = Path(args.dir).resolve()
    if not root.is_dir():
        print(f"not a dir: {root}", file=sys.stderr)
        return 1

    wanted = [c.strip() for c in args.only.split(",") if c.strip()]
    any_run = False
    failures = 0

    for cat in wanted:
        plan = None
        for detectors, cmd in CHECKS.get(cat, []):
            if detect(root, detectors):
                plan = cmd
                break
        if not plan:
            print(f"[{cat}] no known project marker in {root.name}/ — skipped")
            continue
        # py_compile special-case: compile changed/all .py files instead of dir
        cmd = list(plan)
        if cmd[:3] == ["python3", "-m", "py_compile"]:
            pys = sorted(str(p) for p in root.rglob("*.py")
                         if not any(s in p.parts for s in ("node_modules", ".venv", "__pycache__")))
            if not pys:
                print("[lint] no .py files — skipped")
                continue
            cmd += pys[:80]

        print(f"[{cat}] $ {' '.join(cmd[:6])}{' …' if len(cmd) > 6 else ''}")
        if args.list:
            continue
        any_run = True
        try:
            r = subprocess.run(cmd, cwd=root, capture_output=True, text=True,
                               timeout=args.timeout)
            ok = r.returncode == 0
            if not ok:
                failures += 1
            tail = (r.stderr or r.stdout).strip().splitlines()[-6:]
            print(f"     -> {'PASS ✅' if ok else f'FAIL ❌ (exit {r.returncode})'}")
            for ln in tail:
                print("       ", ln[:150])
        except subprocess.TimeoutExpired:
            failures += 1
            print(f"     -> TIMEOUT ❌ ({args.timeout}s)")

    if args.list:
        print("dry-run complete")
        return 0
    if not any_run:
        print("nothing ran — add project markers (package.json, pyproject.toml …)")
        return 2
    print(f"\n{'ALL CHECKS PASSED ✅' if failures == 0 else f'{failures} CHECK(S) FAILED ❌'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
