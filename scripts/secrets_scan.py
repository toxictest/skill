#!/usr/bin/env python3
"""Scan files for hardcoded secrets (defensive, own code only) — super-skill security playbook.

Usage:  secrets_scan.py PATH [PATH...]   (files or dirs; skips .git/node_modules)
Output: file:line  PATTERN-TYPE  redacted-match
Exit:   0 = clean, 1 = findings (authorized/defensive review of YOUR code).
"""
import re
import sys
from pathlib import Path

PATTERNS: list[tuple[str, re.Pattern]] = [
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("OPENAI_KEY", re.compile(r"sk-(?:proj-)?[A-Za-z0-9]{20,}")),
    ("GOOGLE_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("HARDCODED_PASSWORD", re.compile(
        r"""(?i)(?:password|passwd|pwd|secret|api[_-]?key)\s*[:=]\s*["'][^"']{8,}["']""")),
    ("HARDCODED_URL_CRED", re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{4,}@")),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".cache"}
EXT = {".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".java", ".php", ".env",
       ".sh", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".txt", ".md"}
MAX_BYTES = 1_500_000


def scan_file(path: Path) -> list[str]:
    out = []
    try:
        if path.stat().st_size > MAX_BYTES:
            return out
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for i, line in enumerate(text.splitlines(), 1):
        for name, pat in PATTERNS:
            if pat.search(line):
                red = re.sub(r"([A-Za-z0-9_-]{6})[A-Za-z0-9_-]+", r"\1…", line.strip())[:110]
                out.append(f"{path}:{i}  {name}  {red}")
                break
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    targets: list[Path] = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            targets.extend(f for f in p.rglob("*")
                           if f.is_file() and not any(set(f.parts) & SKIP_DIRS for _ in [0])
                           and f.suffix in EXT or f.name == ".env")
        elif p.exists():
            targets.append(p)
    findings: list[str] = []
    for f in targets:
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        findings += scan_file(f)
    if findings:
        print(f"FOUND {len(findings)} potential secret(s) — rotate any real ones:\n")
        for line in findings:
            print(" ", line)
        return 1
    print(f"CLEAN — {len(targets)} file(s) scanned, no hardcoded secrets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
