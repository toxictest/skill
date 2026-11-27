# 86. Skill supply-chain safety (ClawHub campaign)

- **URL**: https://virtualuncle.com/agent-skills-marketplace-skills-sh-2026/
- **Category**: security
- **Verdict**: ✅ core reference

## What it is
Jan-2026 coordinated malware campaign: 335 malicious skills on ClawHub exfiltrating API keys, wallet credentials, browser passwords. Trust model: skills.sh = install-count only; agentskill.sh/SkillDirectory = scanning; rule = read SKILL.md before install (30s).

## How super-skill uses it
Hardened SKILL.md section 6: never install a third-party skill without reading its SKILL.md; prefer vetted directories; treat unvetted skills like untrusted code.

## Status in this skill
Covered in ANALYSIS.md (section mapping) and routed via the matching
playbook under `playbooks/`. Regenerate this file with
`python3 scripts/build_sources.py`.
