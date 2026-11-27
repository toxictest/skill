---
name: ig-caption
description: Write and lint Instagram captions — hook-first variants, a focused hashtag block, and compliance checks against IG limits (2200 chars, shadowban-risk tags). Use for "caption for my post", "Instagram captions", "hashtags", "make this post catchy", or any request to write/improve caption text for a feed post or Reel.
---

# ig-caption

A caption is a hook plus a reason to stop. The first line lives above the
fold — if it does not earn the second line, nothing below it matters.

## Workflow

1. **Ask two things** (one round max): the post's visual/topic, and the
   audience. If both are in the request, skip asking.
2. **Generate**:
   ```bash
   python3 ig_caption.py --topic "<topic>" --audience "<audience>" \
       --tone <curious|warm|bold> --variants 3 --out caption.md
   ```
3. **Pick the best** by hook score + fit to the actual image/video.
   The script lints: 2200-char caption limit, 3–15 hashtags (30 is the
   hard cap; small sets rank better), hook ≤ 125 chars for the fold,
   and drops known shadowban-risk tags.
4. **Deliver** the chosen caption + hashtag block in chat; if a file was
   written, present it. Never pad with hashtags the platform may throttle.

## Rules

- Hook first, always — one line, ≤ 125 chars, specific (number, name,
  contradiction), never "check this out".
- Hashtags serve discovery: 3–15, mix of broad + niche, all real and
  checked against the banned list in the script.
- Tone matches the creator's voice profile if one exists (see
  youtube-skills voice.md convention — same idea for IG).
- No engagement-bait ("like for like", "follow for follow") — the
  script's banned list is the floor, not the ceiling.

## Arena mode (Arena.ai Agent Mode)

This skill runs on Arena.ai too — no slash command needed. The agent
auto-routes to this SKILL.md from the task, runs the bundled script with
`bash`, and delivers outputs (caption file, cover image, plan) via
`present_file`. No posting happens here — the skill writes, the user
publishes on Instagram.
