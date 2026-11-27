#!/usr/bin/env python3
"""Auto-choose the right playbook for a task — super-skill auto-router.

Usage:
  python3 choose_playbook.py "task text"
  echo "task text" | python3 choose_playbook.py
  python3 choose_playbook.py --explain "task text"   # show all scores

Output: ROUTE line (playbook path) + reason. Used by SKILL.md §1 AUTO-MODE
when the user drops a direct task without mentioning the skill.
Also usable standalone to preview how a task will be classified.
"""
import re
import sys
from pathlib import Path

# playbook -> weighted keyword sets (Hinglish + English)
RULES: dict[str, list[tuple[str, int]]] = {
    "research-web": [
        ("research", 3), ("find out", 3), ("search", 2), ("sources", 3),
        ("cite", 3), ("citation", 3), ("compare", 2), ("latest", 2),
        ("news", 2), ("scrape", 3), ("crawl", 3), ("dhoond", 3),
        ("dhundh", 3), ("pata kar", 3), ("kya hai", 2), ("kaun sa", 2),
        ("which is better", 3), ("review of", 2), ("web se", 3),
        ("documentation", 2), ("docs", 1), ("overview", 1),
    ],
    "coding-dev": [
        ("code", 3), ("build", 2), ("website", 3), ("webpage", 3),
        ("landing page", 3), ("app bana", 4), ("api", 3), ("bug", 3),
        ("refactor", 3), ("function", 2), ("script", 2), ("python", 2),
        ("javascript", 2), ("react", 2), ("node", 1), ("deploy", 2),
        ("repo", 2), ("repository", 2), ("test chal", 3), ("lint", 3),
        ("program", 2), ("cli tool", 3), ("database", 1), ("sql query", 2),
        ("bana do", 1), ("banao", 1), ("develop", 3), ("implement", 3),
    ],
    "documents": [
        ("pdf", 3), ("excel", 3), ("word", 2), ("docx", 4), ("xlsx", 4),
        ("pptx", 4), ("powerpoint", 4), ("presentation", 3), ("slide", 3),
        ("spreadsheet", 3), ("document", 2), ("report bana", 4),
        ("convert", 2), ("ocr", 4), ("table bana", 3), ("cv bana", 4),
        ("resume", 3), ("invoice", 3), ("file bana", 2),
    ],
    "security": [
        ("security", 4), ("vulnerability", 4), ("pentest", 4), ("scan", 2),
        ("hack", 3), ("ctf", 4), ("malware", 4), ("phishing", 3),
        ("hardening", 4), ("security review", 5), ("audit", 2),
        ("semgrep", 4), ("owasp", 4), ("xss", 4), ("sql injection", 5),
        ("exploit", 3), ("threat", 3), ("virus", 3), ("breach", 4),
        ("secure kar", 4), ("check kar security", 5),
    ],
    "data-ai-memory": [
        ("analyze", 3), ("analysis", 3), ("csv", 4), ("dataset", 4),
        ("data", 2), ("chart", 3), ("graph", 2), ("dashboard", 4),
        ("statistics", 3), ("pandas", 4), ("rag", 4), ("embedding", 4),
        ("vector", 2), ("llm", 3), ("ai agent", 4), ("memory", 2),
        ("mcp", 4), ("prompt", 2), ("model", 1), ("trend", 2),
        ("insight", 3), ("kaise perform", 3),
    ],
    "automation-systems": [
        ("automate", 4), ("automation", 4), ("browser", 2), ("bot", 3),
        ("workflow", 3), ("n8n", 4), ("server", 2), ("linux", 3),
        ("ansible", 4), ("ssh", 3), ("cron", 4), ("service", 2),
        ("terminal", 2), ("shell", 2), ("deploy server", 4),
        ("self-host", 4), ("schedule", 3), ("chala do", 2),
    ],
    "creative-media": [
        ("image", 3), ("logo", 4), ("poster", 4), ("thumbnail", 4),
        ("banner", 4), ("illustration", 4), ("picture", 3), ("photo", 3),
        ("video", 4), ("voice", 4), ("audio", 4), ("narration", 4),
        ("design", 3), ("avatar", 4), ("thumbnail bana", 5),
        ("gana", 4), ("sing", 3), ("font", 2), ("color palette", 4),
        ("banao image", 5), ("creative", 2),
        ("reel", 4), ("shorts", 4), ("podcast", 4), ("storyboard", 4),
        ("explainer", 3), ("subtitle", 4), ("voiceover", 4), ("slideshow", 4),
    ],
    "video-youtube": [
        ("youtube", 5), ("yt studio", 5), ("seo", 4), ("srt", 5),
        ("upload video", 5), ("video upload", 5), ("chapters", 4),
        ("end screen", 5), ("pinned comment", 5), ("monetize", 5),
        ("channel", 4), ("subscriber", 4), ("playlist", 3),
        ("video seo", 6), ("title options", 5), ("video boost", 6),
        ("caption", 3),
    ],
}

# generic words that should NOT decide a route alone
NOISE = {"karo", "kar", "do", "bana", "banao", "ye", "yeh", "mera", "mere",
         "liye", "ek", "aaj", "please", "ka", "ki", "ke", "me", "mein",
         "with", "for", "the", "a", "an", "and", "of", "my", "me", "this"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score(task: str) -> dict[str, tuple[int, list[str]]]:
    t = normalize(task)
    results: dict[str, tuple[int, list[str]]] = {}
    for playbook, keywords in RULES.items():
        hits: list[str] = []
        total = 0
        for kw, weight in keywords:
            if kw in t:
                hits.append(kw)
                total += weight
        results[playbook] = (total, hits)
    return results


def main() -> int:
    args = sys.argv[1:]
    explain = "--explain" in args
    args = [a for a in args if a != "--explain"]

    if args:
        task = " ".join(args)
    else:
        task = sys.stdin.read()
    if not normalize(task):
        print("Usage: choose_playbook.py [--explain] \"task text\"", file=sys.stderr)
        return 1

    results = score(task)
    ranked = sorted(results.items(), key=lambda kv: kv[1][0], reverse=True)
    best_play, (best_score, best_hits) = ranked[0]

    if explain:
        print(f"task: {task}\n")
        for name, (sc, hits) in ranked:
            if sc:
                print(f"  {sc:>3}  {name:<20} hits={hits}")
        print()

    if best_score == 0:
        print("ROUTE: SKILL.md  (no domain keyword matched — use universal workflow + router table)")
        print("REASON: no playbook keywords found; classify manually via SKILL.md §3")
        return 2

    # show ties (within 30% of best and nonzero)
    ties = [n for n, (s, _) in ranked[1:] if s and s >= best_score * 0.7 and best_score - s <= 3]
    print(f"ROUTE: playbooks/{best_play}.md")
    reason = f"matched {best_hits} (score {best_score})"
    if ties:
        reason += f" | also consider: {', '.join(ties)}"
    print(f"REASON: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
