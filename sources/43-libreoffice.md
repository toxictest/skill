# 43. LibreOffice/LibreOffice

- **URL**: https://github.com/LibreOffice/LibreOffice
- **Category**: documents
- **Verdict**: 🟡 useful tool (needs install)

## What it is
Full office suite with headless `soffice` converter.

## How super-skill uses it
scripts/soffice_convert.sh wraps it; not preinstalled — apt install libreoffice-core.

## Status in this skill
Covered in ANALYSIS.md (section mapping) and routed via the matching
playbook under `playbooks/`. Regenerate this file with
`python3 scripts/build_sources.py`.
