# super-skill

Universal **auto-routing task skill** for Arena Agent Mode (and any Agent Skills
runtime). Ek entry point (`SKILL.md`) jo kisi bhi task ko sahi domain playbook
pe route karta hai, phir plan → execute → verify → deliver ka workflow chalta hai
quality aur safety guardrails ke saath. Hinglish aur English dono me kaam karta hai.

## Kya hai isme

```
SKILL.md          ← entry point: auto-router + universal workflow + guardrails
ANALYSIS.md       ← audit of all 90 reference sources (5 batches)
USAGE-ARENA.md    ← how to drive this skill on Arena.ai (Hinglish quickstart)
MANIFEST.json     ← sha256 inventory (integrity: make_manifest.py --verify)
playbooks/        ← 8 domain playbooks (load on demand, progressive disclosure)
scripts/          ← tested, runnable helpers (see below)
sources/          ← 1 reference file per source link (README = index)
design/           ← shipped design demos + demo.mp4 (video pipeline proof)
brand/            ← trilingual brand kit + SVG logos
```

## Install / deps

Most scripts **Python stdlib only** pe chal jaate hain. Media/office/chart
helpers ke liye optional deps:

```bash
pip install -r requirements.txt
```

## Usage

Koi prefix nahi chahiye — seedha task likho, skill khud route karegi:

```bash
python3 scripts/choose_playbook.py "ye CSV ka analysis karo"
# → ROUTE: playbooks/data-ai-memory.md
# → REASON: matched ['csv', 'analysis', 'karma'] (score 8)
```

Bundled scripts: `office_validate.py`, `csv_profile.py`, `chart.py`,
`check_urls.sh`, `link_extract.py`, `html_template.py`, `git_commit_msg.py`,
`run_checks.py`, `secrets_scan.py`, `security_headers.py`, `health_check.py`,
`palette.py`, `make_video.py`, `docx_report.py`, `new_skill.sh`,
`soffice_convert.sh`, `concat_video.py`, `make_srt.py`, `youtube_seo.py`,
`make_manifest.py`, `selftest.py`. Pura list aur playbook mapping `SKILL.md §4` me hai.

## Verify (before shipping any change)

```bash
python3 scripts/selftest.py --fast        # full package smoke test
python3 scripts/selftest.py              # + video demo
python3 scripts/make_manifest.py --verify # tamper/partial-copy check
```

## Repo layout note

Pehle repo ek zip upload thi (`super-skill.zip`). Ab skill files directly repo
root me hain — standard Agent Skill layout, cloning ke baad `SKILL.md` seedhe
milegi, zip redundant tha isliye removed.
