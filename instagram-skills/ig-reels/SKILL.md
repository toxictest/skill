---
name: ig-reels
description: Validate and package Instagram Reels — check 9:16 specs and duration, extract a cover frame with UI safe zones marked, and write a publish-ready plan. Use for "make a reel", "check this video for Instagram", "reel cover", "convert this video to Reels", or any Reels packaging request.
---

# ig-reels

A Reel that fails the spec fails silently — wrong aspect crops the cover,
over-length gets truncated, text under the UI is unreadable. Validate
before anything is posted.

## Workflow

1. **Source the video**: render 9:16 with video-studio
   (`vs_plan.py --width 1080 --height 1920`), or repurpose an existing
   clip. Keep it ≤ 90 s unless the brief demands more.
2. **Validate + cover**:
   ```bash
   python3 ig_reels.py --video reel.mp4 --title "<hook text>" \
       --out cover.jpg [--at 1.5]
   ```
   It checks aspect ratio (9:16), duration ceiling, audio presence, decode
   integrity, and writes `cover.jpg` with safe zones drawn in red plus
   `cover.plan.md` (reels_plan).
3. **Fix anything flagged**: re-render with the right aspect; cut length;
   add audio. Re-run until verdict is PASS.
4. **Pair with ig-caption** for the caption + hashtags, and deliver:
   `reel.mp4`, `cover.jpg`, the caption, and the plan.

## Rules

- **Safe zones are hard**: no text/faces in the top 14% (profile UI),
  bottom 25% (caption/CTA UI) or right 20% (action buttons). The cover
  the script makes shows them — keep all text inside the clear center.
- 9:16 at 1080x1920 is the target; a 0.45–0.56 aspect ratio is tolerated
  only if it will be center-cropped deliberately.
- Reels with sound outperform silent ones — a Reel with no audio track is
  a warning, not a pass.
- Nothing gets published by the skill — the user posts.

## Arena mode (Arena.ai Agent Mode)

This skill runs on Arena.ai too — no slash command needed. The agent
auto-routes to this SKILL.md from the task, runs the bundled script with
`bash`, and delivers outputs (caption file, cover image, plan) via
`present_file`. No posting happens here — the skill writes, the user
publishes on Instagram.
