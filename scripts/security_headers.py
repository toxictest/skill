#!/usr/bin/env python3
"""Check security headers of a URL you own/authorize — super-skill security playbook (defensive).

Usage:  security_headers.py URL [--full]
Output: markdown pass/fail table for HSTS, CSP, X-Frame, XCTO, Referrer, Permissions, XSS-Protection.
Exit:   0 = all key headers present, 1 = gaps found.
"""
import argparse
import sys
import urllib.request

CHECKS = [
    ("Strict-Transport-Security", "HSTS", True),
    ("Content-Security-Policy", "CSP", True),
    ("X-Content-Type-Options", "nosniff", True),
    ("X-Frame-Options", "DENY|SAMEORIGIN", True),
    ("Referrer-Policy", None, False),
    ("Permissions-Policy", None, False),
    ("X-XSS-Protection", "0|1; mode=block", False),
]
UA = {"User-Agent": "Mozilla/5.0 (super-skill header-check; authorized targets only)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--full", action="store_true", help="print all response headers")
    args = ap.parse_args()

    try:
        req = urllib.request.Request(args.url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            hdrs = dict(r.headers)
            code = r.status
    except Exception as exc:  # noqa: BLE001
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    if args.full:
        for k, v in hdrs.items():
            print(f"{k}: {v}")
        print()

    print(f"# Header check: {args.url} (HTTP {code})\n")
    print("| Header | Status | Value |")
    print("|---|---|---|")
    missing_required = 0
    for name, expect, required in CHECKS:
        val = next((v for k, v in hdrs.items() if k.lower() == name.lower()), None)
        if val is None:
            mark = "❌ MISSING" if required else "⚠️ missing"
            if required:
                missing_required += 1
            print(f"| {name} | {mark} | — |")
        else:
            print(f"| {name} | ✅ | `{val[:60]}` |")
    verdict = "GAPS FOUND" if missing_required else "PASS (key headers present)"
    print(f"\n**Verdict: {verdict}** — fix missing headers at your server/WAF config.")
    return 1 if missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
