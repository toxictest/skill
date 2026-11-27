#!/usr/bin/env python3
"""Extract links from a web page — super-skill research-web playbook.

Usage:  link_extract.py URL [--keyword KW] [--limit N]
Output: markdown list of unique links (text → url), optional keyword filter.
"""
import argparse
import re
import sys
import urllib.request
from html import unescape
from urllib.parse import urljoin, urlparse

UA = {"User-Agent": "Mozilla/5.0 (super-skill link-extract)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--keyword", default=None, help="filter link text/url contains KW")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    try:
        req = urllib.request.Request(args.url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 1

    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                         html, re.I | re.S):
        href, inner = m.group(1).strip(), m.group(2)
        text = unescape(re.sub(r"<[^>]+>", " ", inner))
        text = re.sub(r"\s+", " ", text).strip()[:80]
        full = urljoin(args.url, href)
        if full.startswith(("javascript:", "mailto:", "#")) or full in seen:
            continue
        if args.keyword:
            kw = args.keyword.lower()
            if kw not in (text + " " + full).lower():
                continue
        seen.add(full)
        pairs.append((text or urlparse(full).path or full, full))
        if len(pairs) >= args.limit:
            break

    print(f"# {len(pairs)} links from {args.url}\n")
    for text, url in pairs[: args.limit]:
        print(f"- [{text}]({url})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
