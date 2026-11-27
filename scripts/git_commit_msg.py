#!/usr/bin/env python3
"""Suggest a conventional-commit message from staged changes — super-skill coding-dev (#84 pattern).

Usage:  git_commit_msg.py            (run inside a git repo with staged changes)
        git_commit_msg.py --scope api
Output: "type(scope): summary" suggestion + body bullets (files changed).
"""
import argparse
import re
import subprocess
import sys


def run(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout


def classify(files: list[str], diff: str) -> str:
    names = " ".join(files).lower()
    added = len(re.findall(r"^\+[^+]", diff, re.M))
    removed = len(re.findall(r"^-[^-]", diff, re.M))
    if re.search(r"test|spec|__tests__", names):
        return "test"
    if re.search(r"docs?/|readme|\.md$", names):
        return "docs"
    if re.search(r"ci/|\.github/|workflow", names):
        return "ci"
    if re.search(r"fix|bugfix", diff.lower()) or "fix" in diff.lower():
        return "fix"
    if added > removed * 3 and added > 20:
        return "feat"
    if removed > added:
        return "refactor"
    return "chore"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default=None, help="scope hint, e.g. api, ui")
    args = ap.parse_args()

    status = run("git", "status", "--porcelain")
    if not status.strip():
        print("nothing staged/changed (git status empty)", file=sys.stderr)
        return 1

    staged = run("git", "diff", "--staged", "--name-only")
    files = [f for f in staged.splitlines() if f.strip()]
    diff_scope = staged if files else run("git", "diff", "--name-only")
    if not files:
        files = [f for f in diff_scope.splitlines() if f.strip()]
    diff = run("git", "diff", "--staged") or run("git", "diff")

    if not files:
        print("no changes found", file=sys.stderr)
        return 1

    typ = classify(files, diff)
    scope = args.scope
    if not scope:
        tops = {f.split("/")[0] for f in files if "/" in f}
        scope = tops.pop() if len(tops) == 1 else None

    # first meaningful added line as summary seed
    added_lines = [l[1:].strip() for l in re.findall(r"^\+.{3,}$", diff, re.M)
                   if l[1:].strip() and not l.startswith("+++")]
    summary = (added_lines[0][:60].rstrip() if added_lines
               else f"update {len(files)} file(s)")
    summary = re.sub(r"^(def |class |import |function |const |let |var )", "", summary)

    head = f"{typ}({scope}): {summary}" if scope else f"{typ}: {summary}"
    print(f"SUGGESTED COMMIT:\n  {head}\n")
    print("BODY:")
    for f in files[:8]:
        print(f"  - {f}")
    if len(files) > 8:
        print(f"  … and {len(files) - 8} more")
    print("\ntypes: feat fix docs style refactor perf test build ci chore")
    return 0


if __name__ == "__main__":
    sys.exit(main())
