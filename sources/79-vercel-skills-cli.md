# 79. vercel-labs/skills (skills.sh)

- **URL**: https://github.com/vercel-labs/skills
- **Category**: meta
- **Verdict**: ✅ core reference

## What it is
Vercel's skills.sh registry + open MIT CLI: 'npm for agent skills'. npx skills add <owner/repo> installs any skill into 20 agents (Claude Code, Cursor, Copilot, Codex...); 57K-90K public skills; install-count leaderboard; find-skills meta-skill has 579K installs.

## How super-skill uses it
THE standard way to fetch a skill onto the user's machine: npx skills add <owner/repo> --skill <name>; use install counts + SKILL.md read as trust signals.

## Status in this skill
Covered in ANALYSIS.md (section mapping) and routed via the matching
playbook under `playbooks/`. Regenerate this file with
`python3 scripts/build_sources.py`.
