#!/usr/bin/env python3
"""Health-check HTTP endpoints and TCP ports — super-skill automation-systems playbook.

Usage:  health_check.py [--http URL ...] [--tcp HOST:PORT ...]
Example: health_check.py --http https://example.com --tcp localhost:8080
Exit:   0 all up, 1 any down.
"""
import argparse
import socket
import sys
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (super-skill health-check)"}


def check_http(url: str, timeout: float) -> tuple[bool, str]:
    t0 = datetime.now(timezone.utc)
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
            return 200 <= r.status < 400, f"HTTP {r.status} in {ms}ms"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)[:80]


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    t0 = datetime.now(timezone.utc)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
            return True, f"open in {ms}ms"
    except OSError as exc:
        return False, str(exc)[:80]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="append", default=[], help="URL to check (repeatable)")
    ap.add_argument("--tcp", action="append", default=[], help="host:port (repeatable)")
    ap.add_argument("--timeout", type=float, default=8.0)
    args = ap.parse_args()

    if not args.http and not args.tcp:
        print("nothing to check — pass --http URL and/or --tcp host:port", file=sys.stderr)
        return 1

    results: list[tuple[str, bool, str]] = []
    for url in args.http:
        ok, info = check_http(url, args.timeout)
        results.append((f"HTTP  {url}", ok, info))
    for spec in args.tcp:
        host, _, p = spec.rpartition(":")
        ok, info = check_tcp(host or "localhost", int(p), args.timeout)
        results.append((f"TCP   {spec}", ok, info))

    print("# Health check\n")
    print("| Target | Status | Detail |")
    print("|---|---|---|")
    all_ok = True
    for label, ok, info in results:
        if not ok:
            all_ok = False
        print(f"| {label} | {'✅ UP' if ok else '❌ DOWN'} | {info} |")
    print(f"\n**Overall: {'ALL UP ✅' if all_ok else 'SOME DOWN ❌'}**")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
