# Analysis of All 90 Sources (78 supplied + 12 curated by research)

Date analyzed: 2026-11-26/27. Batch 1: #1–65 (supplied); Batch 2: #66–71
(supplied); Batch 3: #72–78 (supplied); **Batch 4: #79–86 — curated by web
research** (skills.sh/Agensi/Qodo/Composio/Taskade roundups, gap analysis);
**Batch 5: #87–90 — AI video skills** (after #59 proved to be a 404).
Method: live fetch + web search verification.
Verdicts: ✅ core reference · 🟡 useful tool (needs install) · ⚠️ caveat ·
⛔ skip.

> **Per-link files**: every source also has its own reference file in
> [`sources/`](sources/README.md) (93 files: 89 numbered entries — #7 never
> existed, #59 verified-dead — plus 4 top-level links). Regenerate with
> `python3 scripts/build_sources.py`.

## A. Skill formats, catalogs & methodology (the "meta" layer)

| # | Source | What it actually is | Verdict | Extracted into this skill |
|---|---|---|---|---|
| — | anthropics/skills | Anthropic's official Agent Skills repo: `SKILL.md` format, template, Office skills (docx/pptx/xlsx/pdf), spec link | ✅ | Folder+frontmatter format, progressive disclosure, OOXML-only rule |
| 2 | agentskills/agentskills | The open **Agent Skills standard** (agentskills.io): SKILL.md = name+description+instructions; discovery→activation→execution | ✅ | Standard structure; ≤1024-char description; name rules (no "claude"/"anthropic") |
| 1 | openai/skills | Codex skills catalog — **DEPRECATED Jun 2026**, moved to openai/plugins | ⛔ | Only its principle: "write once, use everywhere" |
| 3 | VoltAgent/awesome-agent-skills | 1,497 hand-picked real-world skills, multi-agent compatible | ✅ | Curation ethos ("no AI-slop"); future source of sub-skills |
| 4 | ComposioHQ/awesome-claude-skills | Curated Claude skills + 832 Composio app-automation skills (Gmail/Slack/GitHub…) | ✅ | connect-apps idea → noted under automation; requires API keys |
| 5 | obra/superpowers | Agentic skills framework + SDD dev methodology (brainstorm→plan→TDD→verify), v7.0.2, 687 commits | ✅ | The Universal Workflow in SKILL.md §2 |
| 6 | github.com/skills | **Not a valid/verified repo** (org/repo doesn't resolve to a known project) | ⚠️ | Ignored |
| — | Masriyan/Claude-Code-CyberSecurity-Skill | 22 production security skills: offensive, defensive, RE, threat intel, purple team, GRC, OT/ICS, LLM security | ✅ | Security playbook structure + ethical scope |
| — | GarethManning/education-agent-skills | 165 evidence-grounded education skills (pedagogy, assessment), Claude/Codex/Hermes | ✅ | "Evidence-grounded" quality bar (cite, don't invent) |
| — | trailofbits/skills | Security research/audit skills (taint-trace, CodeQL/Joern, lean proofs) | ✅ | Verify-with-evidence habit; audit workflow |
| — | Google Drive file `1DaWqC-OY…` | **Could not fetch (HTTP 500)** — Drive view links need auth/JS; re-share as direct/downloadable link if you want it analyzed | ⚠️ | Not incorporated |

## B. Research & Web Browsing (8–14)

| # | Source | Verdict | Note |
|---|---|---|---|
| 8 | firecrawl/firecrawl | 🟡 | LLM-ready crawling API; needs API key/host |
| 9 | browser-use/browser-use | 🟡 | Python agent that drives a real browser |
| 10 | vercel-labs/agent-browser | 🟡 | Lightweight browser agent for AI |
| 11 | apify/crawlee | 🟡 | Scraping library (Playwright/HTTP) |
| 12 | ScrapeGraphAI/scrapegraph-ai | 🟡 | AI-graph-based scraper |
| 13 | unclecode/crawl4ai | 🟡 | Open-source, LLM-friendly crawler — best free default |
| 14 | assafelovic/gpt-researcher | 🟡 | Autonomous multi-source research agent |
| — | duplicates | ⚠️ | browser-use (#9/#22) and agent-browser (#10/#23) listed twice |

**Skill takeaway**: native `web_search`+`fetch_page` cover most tasks;
escalate to crawl4ai/gpt-researcher only for bulk crawling (see
`playbooks/research-web.md`).

## C. Coding & Development (15–21)

| # | Source | Verdict | Note |
|---|---|---|---|
| 15 | All-Hands-AI/OpenHands | 🟡 | Autonomous dev agent (heavy, needs own runtime) |
| 16 | Aider-AI/aider | 🟡 | CLI pair-programmer, git-native |
| 17 | SWE-agent/SWE-agent | 🟡 | Research-grade issue→patch agent |
| 18 | continuedev/continue | 🟡 | IDE AI assistant |
| 19 | TabbyML/tabby | 🟡 | Self-hosted Copilot alternative |
| 20 | patchwork-body/patchwork | 🟡 | Multi-file AI code editing |
| 21 | anthropics/claude-code | ⚠️ | Claude Code CLI — the platform this skill already runs on; not an add-on here |

**Skill takeaway**: I do the coding natively (bash/files/preview); these are
fallbacks for very large jobs — recommend, don't auto-install.

## D. Computer & Browser Automation (22–27)

| # | Source | Verdict | Note |
|---|---|---|---|
| 22–23 | browser-use, agent-browser | dup | See §B |
| 24 | microsoft/PowerToys | ⚠️ | **Windows desktop** utility — irrelevant to Linux sandbox; user-machine only |
| 25 | StagehandAI/Stagehand | 🟡 | AI web automation SDK (Playwright-based) |
| 26 | n8n-io/n8n | 🟡 | Workflow automation (self-host, node-based) |
| 27 | Activepieces/activepieces | 🟡 | Open-source Zapier alternative |

## E. Cybersecurity & Ethical Hacking (28–38)

| # | Source | Verdict | Note |
|---|---|---|---|
| 28 | projectdiscovery/nuclei | 🟡 | Template vuln scanner — authorized targets only |
| 29 | zaproxy/zaproxy | 🟡 | OWASP ZAP DAST scanner |
| 30 | semgrep/semgrep | 🟡 | SAST — safe default for code review |
| 31 | trailofbits/skills | ✅ | See §A |
| 32 | OWASP WSTG | ✅ | Web testing checklist (reference, not tool) |
| 33 | OWASP ASVS | ✅ | App security requirements standard |
| 34 | OWASP MASVS | ✅ | Mobile app security standard |
| 35 | ffuf/ffuf | 🟡 | Fast fuzzer — authorized only |
| 36 | mitmproxy/mitmproxy | 🟡 | Interactive proxy — own traffic only |
| 37 | sqlmapproject/sqlmap | ⚠️ | SQLi exploitation — **permission-gated**, labs/CTF only |
| 38 | byt3bl33d3r/CrackMapExec | ⚠️ | Now "NetExec"; Active-Directory attacks — **permission-gated, red-team only** |

**Skill takeaway**: `playbooks/security.md` hard-rules: defensive/authorized
scope, lab-first, refuse malware/unauthorized attacks.

## F. Documents (39–44)

| # | Source | Verdict | Note |
|---|---|---|---|
| 39 | microsoft/markitdown | 🟡 | Office/PDF → Markdown converter |
| 40 | docling-project/docling | 🟡 | Document → structured JSON (IBM) |
| 41 | PaddlePaddle/PaddleOCR | 🟡 | OCR for scans/images |
| 42 | Unstructured-IO/unstructured | 🟡 | Ingestion for RAG pipelines |
| 43 | LibreOffice | ✅ (installable) | `soffice` headless conversions in sandbox |
| 44 | ONLYOFFICE/DocumentServer | ⚠️ | Full server suite — overkill for sandbox |

**Skill takeaway**: python-docx/openpyxl/python-pptx + markitdown + LibreOffice
cover the playbook; matches anthropics Office-skills approach.

## G. Data, Analytics & AI (45–50)

| # | Source | Verdict | Note |
|---|---|---|---|
| 45 | qdrant/qdrant | 🟡 | Vector DB for RAG; needs server/docker |
| 46 | run-llama/llama_index | 🟡 | RAG/data-framework |
| 47 | langchain-ai/langgraph | 🟡 | Stateful agent graphs — modern default |
| 48 | FlowiseAI/Flowise | 🟡 | Low-code visual agent builder |
| 49 | microsoft/semantic-kernel | ⚠️ | Enterprise/MS-stack; heavy |
| 50 | crewAIInc/crewAI | 🟡 | Role-based multi-agent orchestration |

All are **build-time recommendations**, not sandbox defaults — advise
architecture, install only if the user commits.

## H. Memory, MCP & Integrations (51–55)

| # | Source | Verdict | Note |
|---|---|---|---|
| 51 | modelcontextprotocol/servers | ✅ | Reference for MCP tools/standard |
| 52 | ComposioHQ/composio | 🟡 | 1000+ app integrations; needs API key |
| 53 | mem0ai/mem0 | 🟡 | LLM long-term memory |
| 54 | Significant-Gravitas/AutoGPT | ⚠️ | Legacy autonomous agent; superseded |
| 55 | langchain-ai/langchain | 🟡 | Chain/agent framework |

**Note**: this Arena session currently has **no connectors connected** —
app tasks start by checking `list_connector_tools`, then guiding connect.

## I. Image, Video & Creative AI (56–60)

| # | Source | Verdict | Note |
|---|---|---|---|
| 56 | comfyanonymous/ComfyUI | 🟡 | Node-based gen UI; needs GPU |
| 57 | lllyasviel/ControlNet | 🟡 | Diffusion control; needs GPU + SD |
| 58 | facefusion/facefusion | ⚠️ | Face-swap — **consent required**, see safety rules |
| 59 | harry-styles/AI-Video-Generator | ⛔ | **404 — repo does not exist** (GitHub API verified 2026-11-26). Name is an SEO keyword for commercial tools (SendFame/Pollo/Opus). **Replaced by real video skills #87–90.** |
| 60 | modelscope/modelscope | 🟡 | ModelScope model hub |

**Skill takeaway**: use native `generate_image` / `generate_speech` first.

## J. Linux, Terminal & System (61–65)

| # | Source | Verdict | Note |
|---|---|---|---|
| 61 | termux/termux-app | ⚠️ | Android-only terminal; user device |
| 62 | ohmyzsh/ohmyzsh | ⚠️ | Shell theme; cosmetic dotfiles |
| 63 | ansible/ansible | ✅ | Config management for user infra |
| 64 | localsend/localsend | ⚠️ | LAN file share; user devices only |
| 65 | fastfetch-cli/fastfetch | ⚠️ | System info; cosmetic |

**Skill takeaway**: ansible is the only one with real operational value for
tasks; the rest are user-machine recommendations.

## K. Batch 2 — six additional sources (66–71)

| # | Source | Verdict | Note |
|---|---|---|---|
| 66 | michael-ltm/linux-server-skill | 🟡 | AI skill → full Linux server panel over SSH: deploy (Node/Java/Python/PHP/Docker), Nginx + Let's Encrypt, WAF (ModSecurity+OWASP CRS), MySQL/PG/Redis/Mongo, monitoring, logs, users, cron; dual-layer session memory. Claude Code plugin (`/plugin install linux-server-skill@linux-server-skill`), also Cursor/OpenClaw. **Feeds `playbooks/automation-systems.md` server section.** |
| 67 | spencerpauly/awesome-cursor-skills | ✅ | Curated Cursor skills list — 65 ready-to-copy `SKILL.md` files under `resources/` (CC0): cursor-native (suggest rules/hooks, visual QA, browser verify), analytics, scaffolding, image-gen. Another discovery catalog alongside VoltAgent. |
| 68 | madebyaris/spec-kit-command-cursor | 🟡 | SDD (Spec-Driven Development) toolkit for Cursor — `/specify` → `/plan` → `/tasks`, v6.0, `sdd-memory` skill, cloud subagents. Complements obra/superpowers planning in `coding-dev.md`. |
| 69 | girijashankarj/cursor-handbook | 🟡 | Open-source rules engine for Cursor: 110 rules/agents/skills/commands as "permanent memory of standards"; claims 30%+ token savings, secret-scan blocks, type-check over 100K-token test runs. Good reference for team coding standards. |
| 70 | ryanmk54/ai-skill-commands | ⚠️ | Personal mini-project (3 commits, 0 stars): Cursor commands + `personal-kanban` skill + chat-log tracking (avoid duplicate work across sessions). Idea useful: session task logs; repo too small to depend on. |
| 71 | marvelayush/Mouse_controller | ⚠️ | **Not a skill** — gyroscope phone-as-mouse project (FastAPI + WebSockets + Android/Next.js, UDP/TCP gyro, AirMouse). Messy `a2–a7` experiment folders. User-device/hardware only; interesting reference for UDP/gyro streaming, irrelevant to sandbox tasks. |

## L. Batch 3 — security skills & discovery indexes (72–78)

| # | Source | Verdict | Note |
|---|---|---|---|
| 72 | strobes-security/web-pentest-sample | 🟡 | Sample pentest skill with exemplary **4-layer architecture**: SKILL.md (6-phase methodology) → scripts/ (Burp-inspired CLI, 12 tools) → lib/ (db/http/output) → project.db (SQLite state/evidence). One-commit sample — read for architecture, not for maintenance. |
| 73 | frendysanusi/agent-pentest-skills | 🟡 | Claude Code pentest skills: OWASP WSTG methodology, curated payloads, **validation gates**, slash-command orchestration, MCP integration, indirect prompt-injection gating, credential redaction in evidence. |
| 74 | hassan-algo/open-sesame | 🟡 | Web + network pentest skill (MIT): attack-surface mapping → WSTG → validated findings → **dual PDF reports** (dev + stakeholder); net-pentest (PTES/NIST 800-115: AD, privesc, pivoting, cloud, containers); Docker Samba AD lab; timed benchmarks (Metasploitable2, Juice Shop). |
| 75 | Eyadkelleh/awesome-skills-security | ✅ | 7 SecLists-based skills (fuzzing, passwords, patterns, payloads, usernames, web-shells, LLM testing) packaged for agents; `npx skills add Eyadkelleh/awesome-skills-security` — explicit authorized-testing/CTF/bug-bounty scope. |
| 76 | github.com/topics/ai-penetration-testing | 🟡 | **Discovery index** (59 repos): strix 77.8k★, shannon 52.4k★ (AI web/API pentester), hexstrike-ai 13.9k★ (MCP → 150+ sec tools), Decepticon 6.8k★. Use for finding new AI-sec tools; nothing to install itself. |
| 77 | NousResearch/hermes-agent/optional-skills | ✅ | Hermes agent's skill library: **191 in-repo skills** (77 bundled + 114 optional: autonomous-ai-agents, blockchain, communication, creative, data-science, devops…). Valuable **authoring standards**: descriptions ≤60 chars one sentence, complete frontmatter (author/license/version/platforms/tags), no machine-local paths, scratch dirs never `/tmp`. |
| 78 | github.com/topics/penetration-testing-tools | 🟡 | **Discovery index** (814 repos): pentagi 35.1k★ (autonomous pentest agents), WhatWeb 7k, Modlishka 5.5k, CDK 4.8k (K8s/Docker). Discovery only — permission-gated tools, see security playbook rules. |

**Batch 3 theme**: pentest skill architecture + standards. Feeds
`playbooks/security.md` (methodology, wordlists, reporting) and skill
authoring standards (Hermes) into future skill edits.

## M. Batch 4 — curated by research to fill skill gaps (79–86)

Gap analysis found: no skill registry/installer, no UI-taste rules, no
review/git-hygiene patterns, no behavioral guardrails, no supply-chain
safety rule. These 8 fix that.

| # | Source | Verdict | Note |
|---|---|---|---|
| 79 | vercel-labs/skills (**skills.sh**) | ✅ | The "npm for skills" — Vercel's open directory + CLI: `npx skills add <owner/repo>` installs into 20 agents (Claude Code, Cursor, Copilot, Codex…), 57K–90K public skills, free, MIT CLI, `find-skills` meta-skill = 579K installs. **Was the biggest missing piece — how to actually fetch any skill.** |
| 80 | anthropics **frontend-design** skill | ✅ | Official design-taste skill (277K+ installs): color, spacing, motion, hierarchy with do/don'ts — "don't ship AI-slop UI". Fills creative/coding UI gap. |
| 81 | forrestchang/andrej-karpathy-skills | 🟡 | "Karpathy Behavioral" — four behavioral rules for agents; fast-growing guardrails file designed to merge into CLAUDE.md. Overlaps our §5 quality bar; useful as external pattern. |
| 82 | garrytan/gstack | 🟡 | "Team-in-a-box" full-stack workflow process skill (top of Taskade 2026 list). Heavy methodology — adopt pieces, not wholesale. |
| 83 | gsd-build/get-shit-done (GSD) | 🟡 | Spec-driven context engineering (64K). Complements superpowers SDD (#5) and spec-kit (#68) — third leg of our PLAN-phase references. |
| 84 | Agensi "12 best skills" catalog | ✅ | Verified pattern bundle: **code-reviewer** (severity: Critical/Warning/Suggestion + security lens), **git-commit-writer** (conventional commits), **pr-description-writer** (test-plan section), **env-doctor**, **humanize-writing** (fills writing gap), **prompt-engineer**, **changelog-generator**, **truth-first** (never claim success without running). |
| 85 | Qodo code-review landscape | ✅ | 5-skill comparison: bundled `/code-review`, mattpocock spec-check, **Trail of Bits differential-review** (security diffs — ties to #31), Superpowers review checkpoints, Qodo engine. Review-before-merge doctrine for coding-dev. |
| 86 | Skill supply-chain safety (ClawHub campaign) | ✅ | Jan-2026: **335 malicious skills** on ClawHub targeted API keys/wallets/browser passwords. Rule adopted: read SKILL.md before install, prefer vetted/heavy-install directories (skills.sh, agentskill.sh scanning). → SKILL.md §6. |

**Batch 4 theme**: operational gaps — discovery/install (79), design taste
(80), guardrails (81), methodologies (82–83), review/git/writing patterns
(84–85), safety (86).

## N. Batch 5 — AI VIDEO skill integration (87–90)

Manual inspection of #59 proved it dead (404) → replaced with **verified
real AI-video skills** + a working in-sandbox video pipeline.

| # | Source | Verdict | Note |
|---|---|---|---|
| 87 | Felo-Inc/agent-video-skills | ✅ | **23 MIT Agent Skills** for video across six workflow stages: Generate (openrouter-video-gen, seedance-video, text-to-video) · Edit · Subtitles/localization · Shorts/thumbnails · motion graphics/Remotion · ads/scripts. Every skill credits its upstream MIT source. Ideal pick-and-mix. |
| 88 | openfilm/openfilm | 🟡 | **9.5K★** open-source video agent (TypeScript): agent writes shots as web pages (`frame(t)`), live co-editing timeline, footage/music/voices, works with Claude Code/Codex. Local install — desktop-app style, heavier. |
| 89 | wangxin6x/AutoVideo-Agent | ✅ | **MIT, local-first, no API key**: Markdown → storyboard → scene manifest → **FFmpeg MP4** + QA report + SRT subtitles; `pip install autovideo-agent`. Pairs perfectly with our bundled `make_video.py`. |
| 90 | Bomx/super-video-maker-skill | 🟡 | Production skill: avatar explainers (HeyGen), Seedance b-roll, OpenAI images, Remotion/HyperFrames templates, Whisper captions, ffmpeg QC — needs API keys/credits; reference for full pipelines. |

**In-sandbox capability added**: `scripts/make_video.py` — images (+ optional
narration WAV/MP3) → H.264 MP4 via bundled static ffmpeg (imageio-ffmpeg);
tested: 3s demo video + audio mux ✅. Pipeline: `generate_speech` → frames
via `generate_image`/PIL → `make_video.py`.

## O. Top patterns distilled into Super Skill

1. **Format** (anthropics + agentskills.io): folder, `SKILL.md`, frontmatter
   `name`+`description`, progressive disclosure, reference files.
2. **Workflow** (obra/superpowers): clarify → plan → execute → verify →
   deliver; small verifiable increments.
3. **Quality** (GarethManning + VoltAgent): evidence-grounded, hand-curated,
   honest about failures.
4. **Safety** (trailofbits + Masriyan + OWASP): authorized/defensive-only
   security, consent for biometrics, permission-gated offensive tools.
5. **Tool tiers**: native Arena tools → installable open-source tools →
   external agents (recommend only). Never assume preinstalled.
