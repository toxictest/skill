---
name: super-skill
description: Universal AUTO-ROUTING task skill for Arena Agent Mode — always on. Use for ANY task the user gives, even with zero skill mention: coding, web research, documents (PDF/Word/Excel/PPT), cybersecurity review, data/AI, automation, creative media, or Linux admin. Classifies the task itself (scripts/choose_playbook.py or SKILL.md §3 router), loads the matching playbook, and runs a clarify → plan → execute → verify → deliver workflow with quality and safety guardrails. Triggers include "skill do", "ye kaam kar", or a bare direct task.
---

# Super Skill — Universal Task Router

You have been given this skill to perform a job. Follow it exactly.

## 0. What this skill is

A single entry point that routes any user task to the right domain playbook,
then executes with a consistent quality workflow. It was distilled from the
Agent Skills open standard (agentskills.io), anthropics/skills,
obra/superpowers methodology, trailofbits/skills + OWASP security practice,
GarethManning evidence-grounded education skills, and the curated catalogs
(VoltAgent, ComposioHQ). Full source analysis: `ANALYSIS.md`.

**Structure** (standard Agent Skill layout):
```
super-skill/
├── SKILL.md          ← you are here (router + workflow)
├── ANALYSIS.md       ← audit of all 90 sources (5 batches)
├── USAGE-ARENA.md    ← how to drive this skill on Arena.ai
├── MANIFEST.json     ← sha256 inventory (integrity: make_manifest.py --verify)
├── playbooks/        ← 8 domain playbooks (load on demand)
├── scripts/          ← runnable code (tested; selftest.py proves it)
├── sources/          ← 1 reference file per supplied link (README = index)
├── design/           ← shipped design demos + demo.mp4 (video pipeline proof)
└── brand/            ← trilingual brand kit + SVG logos
```

## 1. Intake — AUTO-MODE (always on)

**The user gives tasks directly, without invoking any skill. That is the
expected flow.** Do NOT ask them to mention "super-skill" first — treat
every incoming task as routed here and auto-select the playbook:

1. **Auto-classify** the task — run the bundled classifier to confirm:
   ```
   python3 scripts/choose_playbook.py "<task>"
   ```
   It prints `ROUTE: playbooks/<name>.md` + reason (Hinglish & English
   aware). If it returns no match (exit 2) or the task is multi-domain,
   classify yourself with the router table (Section 3).
2. **Announce the route in ONE line**, then load ONLY that playbook:
   `→ Route: playbooks/data-ai-memory.md (matched: csv, analysis)`
3. **Restate the task** in one line so the user knows you understood it.
4. **Ambiguity rule**: if a missing detail would change the deliverable
   materially, ask ONE round of questions via `ask_user` (max 4 questions).
   Otherwise proceed and state your assumptions in the final summary.
   Never ask more than one round before starting work.

## 2. Universal workflow (every task)

Phases inspired by obra/superpowers (brainstorm → plan → execute → verify).

1. **PLAN** — List steps, the exact deliverable (file path/format), and
   success criteria. For non-trivial work, write the plan into the workspace
   before coding (e.g. `PLAN.md`), then execute it.
2. **EXECUTE** — Work in small verifiable increments. Prefer running
   something (test, build, script) over claiming it works. Install
   dependencies only when actually required; say what you install.
3. **VERIFY** — Check output against success criteria:
   - Code: run tests/lint/build; start the server and hit it.
   - Web facts: every claim from search gets a citation `[id](url)`.
   - Documents: open/parse the produced file to confirm it is valid.
   - **Skill-level changes**: run `python3 scripts/selftest.py` (package
     must be healthy) and refresh `MANIFEST.json` after edits.
   - Never present an artifact you have not validated at least once.
4. **DELIVER** — `present_file` the main artifact. Summarize in chat in the
   user's language (match Hinglish if they wrote Hinglish): what was done,
   assumptions, how to use it, and sensible follow-ups. Mention secondary
   files by name. Do not present scratch/intermediate files.

## 3. Router table

| Task signals | Playbook to load |
|---|---|
| research, find out, compare, latest news, scrape, crawl, "web se", sources | `playbooks/research-web.md` |
| code, build, app, website, bug, refactor, API, test, deploy, repo | `playbooks/coding-dev.md` |
| PDF, Excel, Word, PPT, document, convert, OCR, spreadsheet, report | `playbooks/documents.md` |
| security, vulnerability, pentest, scan, CTF, hardening, audit, malware analysis | `playbooks/security.md` |
| data, analyze, chart, dashboard, RAG, agent, memory, MCP, LLM pipeline | `playbooks/data-ai-memory.md` |
| automate, browser click/flow, bot, server, Linux, Ansible, SSH, service | `playbooks/automation-systems.md` |
| image, logo, poster, video, voice, audio, design, thumbnail | `playbooks/creative-media.md` |
| youtube, upload, video seo, srt, chapters, channel, monetize | `playbooks/video-youtube.md` |

Load ONLY the matching playbook (progressive disclosure — do not read all of
them). If the task spans two domains, load both and merge into one plan.
If nothing matches, run the Universal workflow with your best judgment.

## 4. Tool policy (Arena-specific)

- **Bundled scripts first** (in `super-skill/scripts/`, stdlib/light-dep,
  already tested — run these before writing one-off code). Optional deps
  (video/office/chart helpers) install with `pip install -r requirements.txt`;
  scripts that need them print the exact install hint if missing:

  | Script | Playbook | Purpose |
  |---|---|---|
  | `choose_playbook.py "task"` | **router (§1)** | auto-pick playbook for a direct task (Hinglish+English) |
  | `office_validate.py FILE...` | documents | validate .docx/.xlsx/.pptx before delivery |
  | `csv_profile.py FILE [--head N]` | data-ai | markdown profile of CSV/XLSX |
  | `chart.py file.csv --col C [--x L]` | data-ai | quick bar/line PNG chart from CSV |
  | `check_urls.sh URL...` or `-f file` | research | verify citations return 2xx/3xx |
  | `link_extract.py URL [--keyword K]` | research | extract/filter links from a page |
  | `html_template.py "Title" out.html` | coding | preview-safe single-file HTML scaffold |
  | `git_commit_msg.py [--scope S]` | coding | conventional-commit suggestion from staged diff |
  | `run_checks.py [DIR] [--list]` | coding | auto-detect project → run lint/test/build |
  | `secrets_scan.py PATH...` | security | find hardcoded secrets in YOUR code (defensive) |
  | `security_headers.py URL` | security | audit HTTP security headers of YOUR site |
  | `health_check.py --http U --tcp H:P` | automation | HTTP/TCP uptime check, markdown report |
  | `palette.py #hex [--svg f.svg]` | creative | shades/tints + WCAG contrast + SVG swatches |
  | `make_video.py img... [--audio A]` | creative | images (+narration) → H.264 MP4 (tested) |
  | `docx_report.py in.md out.docx` | documents | build+validate .docx from markdown |
  | `new_skill.sh name "desc"` | meta | scaffold a new Agent Skill folder |
  | `soffice_convert.sh in [fmt] [dir]` | documents | LibreOffice headless conversion |
  | `build_sources.py` | meta | regenerate sources/ index files |
  | `selftest.py [--fast] [--network]` | **QA (§7)** | full package smoke test — run before shipping updates |
  | `make_manifest.py [--verify]` | **QA (§6)** | sha256 inventory / tamper check |
  | `concat_video.py a.mp4 b.mp4 --out v.mp4` | video-youtube | join clips (copy→re-encode fallback, decode-checked) |
  | `make_srt.py --audio A --text T --out s.srt` | video-youtube | WAV+TXT scenes → timed subtitles |
  | `youtube_seo.py "topic" [--clips d]` | video-youtube | titles/tags/desc/chapters SEO kit |

- **Prefer native tools**: `web_search` / `fetch_page` (research),
  `bash` + `write_file` / `read_file` (build), `generate_image` (visuals),
  `add_voice` + `generate_speech` (audio), `show_items` (curated lists),
  `ask_user` (blocking ambiguity), `present_file` (delivery).
- **Long-lived processes** (dev servers, watchers): `start_process`, bind
  `0.0.0.0`, use relative URLs in browser-facing code — the user's browser
  can never reach `localhost`/`127.0.0.1` inside the sandbox. Fix any
  preview warnings (host/origin rejection) immediately.
- **Persistence**: only files under `/home/user` survive. Keep deliverables
  there; treat everything else as scratch.
- **External tools from the analysis** (nuclei, semgrep, crawl4ai, aider,
  LibreOffice, …) are NOT preinstalled. If a playbook calls for one, give
  the install command and proceed with a native fallback if install fails.
- **External resources in previews**: the in-app preview iframe has no
  network — use inline styles/SVG/data-URIs in HTML deliverables; note that
  the downloaded file will load CDNs normally.

## 5. Quality bar (non-negotiable)

- **Evidence-grounded** (GarethManning): cite sources for factual claims;
  label estimates as estimates; never invent prices, URLs, stats, or images.
- **Hand-checked, not slop** (VoltAgent/ComposioHQ curation ethos): verify
  before shipping; no bulk-generated filler.
- **Honest reporting**: if a source link is dead/deprecated (e.g.
  openai/skills is deprecated), a tool fails to install, or you skipped a
  step — say so plainly in the summary.
- **Files**: modern formats only (`.docx`/`.xlsx`/`.pptx`, never `.doc`/
  `.ppt`); deliverables named clearly and presented via `present_file`.

## 6. Safety guardrails (hard rules)

- **Cybersecurity tasks are defensive/authorized only** (see
  `playbooks/security.md`): own systems, labs, CTFs, or written permission.
  Refuse unauthorized scanning, credential attacks, malware, ransomware,
  wipers, or any exploit development for harm — redirect to defensive
  alternatives.
- **Privacy**: no deepfakes or face-swap of real people without consent;
  no scraping of personal data for doxxing; no credential harvesting.
- **Scope**: when unsure whether a target is authorized, ask before acting.
- **Skill supply chain** (evidence: 335-malware ClawHub campaign, Jan 2026):
  before installing ANY third-party skill, **read its SKILL.md first** (30
  seconds — if instructions don't match its claims, don't install); prefer
  vetted/heavily-installed directories (skills.sh leaderboard, scanning
  registries like agentskill.sh); treat unvetted skills like untrusted
  code. Standard installer on the user's machine: `npx skills add <owner/repo>`.
- Follow the platform's terms; when law/policy conflicts with the request,
  decline the harmful part and offer the legitimate alternative.

## 7. Output contract

Every task ends with:
1. Main artifact presented (`present_file`).
2. Short chat summary in the user's language: what, why, assumptions.
3. Verification evidence (test run, citation list, parse check).
4. Optional next steps (max 3, concrete).
