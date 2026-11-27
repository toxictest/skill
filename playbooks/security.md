# Playbook: Cybersecurity (Defensive & Authorized Only)

**Triggers**: security, vulnerability, pentest, scan, hardening, audit,
CTF, malware analysis, OWASP, "check kar lo".

## HARD RULES — read before anything else

1. **Scope = your own systems, local labs, CTFs, or written permission.**
   If target ownership/authorization is unclear → STOP and ask.
2. **Refuse**: unauthorized scanning or access, credential attacks against
   real accounts, malware/ransomware/wipers, exploit development for harm,
   botnets, phishing kits, tracking/doxxing. Offer the defensive alternative.
3. **Tools like sqlmap (#37) and NetExec/CrackMapExec (#38) are
   permission-gated** — local labs/CTF only; never point at third-party
   infrastructure.
4. Report findings honestly: severity + evidence + remediation; no fear
   inflation, no claiming exploits you didn't verify.

## Safe default workflow (code/app review)

1. **Scope**: what am I reviewing (repo path, provided file, local app)?
2. **SAST pass** — `semgrep --config auto <path>` (install:
   `pip install semgrep`); or manual review with OWASP Top 10 lens.
3. **Checklist** — map findings to **OWASP ASVS** (#33) / **WSTG** (#32)
   categories; mobile → **MASVS** (#34).
4. **Dynamic test (local apps only)** — start the app in sandbox, probe
   with `ffuf`/ZAP if installed; traffic inspection via `mitmproxy` on your
   own sessions.
5. **Report** — table: Finding | Severity (CVSS-ish) | Evidence |
   Remediation | Reference (OWASP id or CVE).

## Tool matrix (authorized use only)

| Layer | Tool | Note |
|---|---|---|
| SAST | semgrep | safest default, CI-friendly |
| DAST | OWASP ZAP | local target |
| Scanning | nuclei | projectdiscovery templates; rate-limit, own assets |
| Fuzzing | ffuf | content discovery on local/authorized targets |
| Proxy | mitmproxy | your own traffic |
| SQLi (lab) | sqlmap | `-u` local lab only |
| AD (lab) | NetExec | lab ranges only |
| Skills packs | trailofbits/skills, Masriyan cyberskill | audit & defense workflows |

## Defensive-first alternatives to offer

- Hardening checklist → ASVS/MASVS + CIS-style review of config files.
- "Is this safe?" (dependency scan) → `pip-audit` / `npm audit` locally.
- Malware analysis → static triage of **file provided by user** in sandbox
  (strings/hash/meta) — no detonation of live samples, no propagation.
- Learning → CTF/lab guidance (DVWA, Juice Shop, HackTheBox on user's own
  subscription) instead of real targets.

## Bundled defensive scripts (run these first)

- `scripts/secrets_scan.py <path>` — hardcoded API keys/passwords/private
  keys in the user's own code (redacted output + rotate advice).
- `scripts/security_headers.py <url>` — HSTS/CSP/XFO/XCTO audit of a site
  the user owns (reports gaps, exit code for CI).

Both are **defensive/own-code only** — never aimed at third-party targets.

## Batch 3 references (pentest skill architecture)

- **Methodology sources** (structure to copy):
  - #72 `web-pentest-sample` — **4-layer architecture**: SKILL.md
    (phases/decision-trees) → scripts/ → lib/ → SQLite evidence DB. The
    methodology layer decides *when*, scripts do *how*.
  - #73 `agent-pentest-skills` — **validation gates** before any finding
    is reported; redact credentials in evidence; gate indirect prompt
    injection from target content.
  - #74 `open-sesame` — **dual reporting**: technical report for devs +
    non-technical PDF for stakeholders; benchmark only on labs
    (Metasploitable2, Juice Shop, Samba AD lab).
- **Wordlists/payloads** — #75 `awesome-skills-security` (SecLists subset:
  fuzzing, passwords, patterns, payloads, usernames, web-shells, LLM
  testing): `npx skills add Eyadkelleh/awesome-skills-security` —
  authorized testing/CTF/bug-bounty scope only.
- **Discovery indexes** — #76 topic `ai-penetration-testing` (59 repos:
  strix, shannon, hexstrike-ai) and #78 topic `penetration-testing-tools`
  (814 repos: pentagi, WhatWeb…). Browse when asked for new tools; every
  result stays under the HARD RULES above.
- **Skill authoring standards** — #77 Hermes optional-skills: descriptions
  ≤60 chars one sentence, complete frontmatter, portable paths, no `/tmp`
  scratch — apply when editing security (or any) skills.

## Output

Findings table + executive summary + remediation priority. State scope and
authorization assumption explicitly at the top of the report.
