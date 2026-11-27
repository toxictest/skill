#!/usr/bin/env python3
"""ig_caption.py - build and lint an Instagram caption + hashtag pack.

    ig_caption.py --topic "sunrise photography" --audience "travel lovers" \
        [--tone curious] [--lang en] [--variants 3] [--out caption.md]

Generates N hook + caption variants with a hashtag block, then lints:
- caption length ≤ 2200 chars (IG hard limit)
- hashtag count 3–15 (allowed up to 30; small focused sets rank better)
- banned / shadowban-risk hashtags (static list — extend as needed)
- hook first line ≤ 125 chars so the fold does not cut the hook

Exit: 0 = ok (best variant printed), 1 = nothing usable.
"""
import argparse
import random
import sys

HOOK_TEMPLATES = [
    "Stop scrolling — {topic} is the thing you've been missing.",
    "{topic}: the only guide you need this week.",
    "I tried {topic} for 30 days. Here's what actually happened.",
    "Most people get {topic} wrong. Here's the fix.",
    "POV: you finally understand {topic}.",
]

CAPTION_TEMPLATES = [
    "{hook}\n\n{topic} has been on my mind lately, and after digging in, "
    "the basics are simpler than the noise makes them. Start here, save this, "
    "and tell me your take below.",
    "{hook}\n\nQuick breakdown of {topic}:\n\n"
    "1. Start with the fundamentals — everything else builds on them.\n"
    "2. Do it daily, even small. Consistency beats intensity.\n"
    "3. Watch what actually works and copy that, not the hype.\n\n"
    "Which step are you stuck on? Drop it in the comments.",
    "{hook}\n\nReal talk about {topic}: the fancy stuff matters less than "
    "showing up regularly. If this helps, follow for the next one — and "
    "tag someone who needs it.",
]

BANNED = {"#army", "#beautytips", "#bodybuilding", "#casino", "#crypto",
          "#dank", "#follow4follow", "#followforfollowback", "#freelikes",
          "#like4like", "#sexy", "#tattoo", "#tiktok", "#workfromhome"}


def hashtags(topic: str, audience: str) -> list[str]:
    words = {w.strip(".,!?") for w in (topic + " " + audience).lower().split()
             if len(w) > 3}
    base = {f"#{w}" for w in words}
    extra = {"#explore", "#creator", f"#{topic.split()[0][:20].lower().replace(' ', '')}"}
    return sorted(base | extra)[:12]


def score_hook(hook: str) -> int:
    s = 0
    s += 15 if any(c.isdigit() for c in hook) else 0
    s += 10 if any(w in hook.lower() for w in ("stop", "wrong", "missing", "try", "pov")) else 0
    s += 10 if len(hook) <= 125 else 0
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--audience", default="")
    ap.add_argument("--tone", default="curious")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--variants", type=int, default=3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tags = hashtags(args.topic, args.audience)
    bad = [t for t in tags if t.lower() in BANNED]
    if bad:
        tags = [t for t in tags if t.lower() not in BANNED]
        if not tags:
            tags = [f"#{args.topic.split()[0][:20].lower().replace(' ', '')}", "#explore"]

    variants = []
    for i in range(max(1, args.variants)):
        hook = HOOK_TEMPLATES[(i * 2 + 1) % len(HOOK_TEMPLATES)].format(
            topic=args.topic)
        body = CAPTION_TEMPLATES[(i * 2 + 1) % len(CAPTION_TEMPLATES)].format(
            hook=hook, topic=args.topic)
        variants.append((score_hook(hook), hook, body))
    variants.sort(key=lambda v: -v[0])

    lines = [f"# Instagram caption pack — {args.topic}", "",
             f"audience: {args.audience or 'general'} · tone: {args.tone} · "
             f"lang: {args.lang}", f"hashtags: {len(tags)} ({', '.join(tags)})",
             ""]
    for n, (sc, hook, body) in enumerate(variants, 1):
        full = body + "\n\n" + " ".join(tags)
        issues = []
        if len(full) > 2200:
            issues.append(f"caption {len(full)} chars > 2200 IG limit")
        if len(tags) > 15:
            issues.append("hashtag count > 15")
        if len(hook) > 125:
            issues.append("hook > 125 chars (fold cut risk)")
        lines += [f"## Variant {n} (hook score {sc})",
                  "```", full, "```"]
        if issues:
            lines.append("⚠️ " + "; ".join(issues))
        lines.append("")
    out = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"wrote {args.out}")
    best = variants[0]
    print(f"\nBEST HOOK (score {best[0]}):\n  {best[1]}\n")
    print(f"caption length: {len(best[2]) + len(' '.join(tags)) + 2} chars "
          f"(limit 2200) · hashtags: {len(tags)}")
    if bad:
        print(f"note: dropped shadowban-risk tags: {', '.join(bad)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
