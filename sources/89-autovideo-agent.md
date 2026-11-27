# 89. wangxin6x/AutoVideo-Agent

- **URL**: https://github.com/wangxin6x/AutoVideo-Agent
- **Category**: creative
- **Verdict**: ✅ core reference

## What it is
MIT local-first markdown-to-video pipeline: script -> storyboard -> scene manifest -> assets -> timeline -> FFmpeg MP4 + QA report + SRT subtitles. No API key needed. pip install autovideo-agent.

## How super-skill uses it
Pairs with bundled scripts/make_video.py — our in-sandbox video renderer; use AutoVideo-Agent for structured multi-scene productions.

## Status in this skill
Covered in ANALYSIS.md (section mapping) and routed via the matching
playbook under `playbooks/`. Regenerate this file with
`python3 scripts/build_sources.py`.
