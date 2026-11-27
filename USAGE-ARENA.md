# How to Use This Repo on Arena.ai — all 4 skill packs

No install, no API keys, no plugins. The whole repo lives in the workspace
and runs on Arena's built-in tools (`bash`, files, `web_search`,
`fetch_page`, `generate_image`, `add_voice` + `generate_speech`,
`start_process`, `present_file`, `ask_user`).

## What's in this repo (4 packs)

| Pack | Folder | Job on Arena |
|---|---|---|
| **super-skill** | root (`SKILL.md`) | universal auto-router: any task → right playbook → plan/execute/verify/deliver |
| **video-studio** | `video-studio/` | REAL video creation: script → scene plan → AI art → voiceover → edited MP4 → QC → thumbnail |
| **youtube-skills** | `youtube-skills/` | 11 channel skills: scripts/hooks, title+thumb linting, retention, chapters, viral research… |
| **instagram-skills** | `instagram-skills/` | Instagram: captions, Reels validation + cover, feed grid planning |

## ⚡ AUTO-MODE — seedha task do, skill khud choose hoga

No skill name, no prefix — **bas direct task likho**. The agent reads the
workspace's SKILL.md files and routes:

```
[seedha task likho — koi prefix nahi]
```

What happens:
1. super-skill's classifier confirms the route:
   `python3 scripts/choose_playbook.py "<task>"`
2. Route announced in one line, matching SKILL.md loads
3. plan → execute → verify → deliver (`present_file`)

### Routing table across all packs

| You type | Routes to |
|---|---|
| `ye CSV ka analysis karo`, `data dashboard banao` | super-skill → `playbooks/data-ai-memory.md` |
| `ek landing page banao`, `bug fix karo` | super-skill → `playbooks/coding-dev.md` |
| `research karo sources ke saath` | super-skill → `playbooks/research-web.md` |
| `resume PDF banao`, `Excel report` | super-skill → `playbooks/documents.md` |
| `security review karo` | super-skill → `playbooks/security.md` |
| `reel banao: [idea]`, `video banao` | **video-studio** (real MP4 pipeline) |
| `youtube script likho`, `hook score karo`, `my retention export read karo`, `chapters bnao` | **youtube-skills** (yt-script / yt-retention / yt-chapters …) |
| `caption likho is post ke liye`, `reel ka cover banao`, `feed grid plan karo` | **instagram-skills** (ig-caption / ig-reels / ig-grid) |

### Copy-paste examples

| You type | What happens |
|---|---|
| `super-skill use karke ye kaam kar: is CSV ka analysis do` | data-ai-memory → `csv_profile.py` → report |
| `reel banao: ek 30 second ka sunrise explainer, English voiceover` | video-studio → full pipeline → MP4 + QC |
| `is idea pe youtube script likho, hook score karke` | yt-script → `hookscore.py` → script + scored hooks |
| `is reel ko instagram ke liye validate karo aur cover banao` | ig-reels → spec check + safe-zone cover.jpg |

## How each pack runs on Arena (tool mapping)

Claude Code concepts → Arena equivalents:

| Claude Code | Arena |
|---|---|
| `/yt-script` slash command | auto-route: agent loads `youtube-skills/yt-script/SKILL.md` itself |
| `~/.claude/skills/` install | skills live in this workspace folder; agent reads them from here |
| `~/.claude/youtube/voice.md` | workspace `voice.md` (repo root) — every yt/ig skill reads it |
| shell / terminal | `bash` tool (same scripts, same commands) |
| reading/writing files | `read_file` / `write_file` tools |
| showing output to the user | `present_file` (main artifact) + chat summary |
| blocking questions | `ask_user` (one round, ≤4 questions) |
| long renders / dev servers | `start_process` (background), bind `0.0.0.0` |

**Voice profile**: `voice.md` at the repo root is the creator's voice —
read it before writing any yt-script / ig-caption output. If it's empty,
ask for three of the user's own videos and infer the voice.

## In a NEW Arena chat

Workspace files persist. If a skill folder is not visible:

1. **Easiest**: attach/paste the relevant `SKILL.md` and say
   *"ye skill follow karo + [task]"* — the agent loads the rest from the
   workspace or follows the SKILL.md alone (each is self-sufficient).
2. **Full setup**: say *"skills folder workspace mein dobara banao"* —
   everything regenerates from this repo.

## What makes it work here (no edits needed)

- Every pack follows the standard Agent Skills layout: `SKILL.md` with
  frontmatter (`name` + `description`) + scripts in the same folder
- super-skill's router + classifier auto-route; each pack's SKILL.md has
  an **"Arena mode"** section telling the agent exactly how to execute
- All scripts are stdlib/light-dep and tested; optional deps via
  `pip install -r requirements.txt`
- Nothing in any pack posts/uploads — skills write, the user publishes

## Verify the install

```bash
python3 scripts/selftest.py --fast          # super-skill: 48/48
python3 video-studio/scripts/vs_selftest.py  # video-studio: 6/6
python3 instagram-skills/ig_selftest.py    # instagram: 3/3
python3 scripts/make_manifest.py --verify  # integrity
```

## Tips

- Hinglish/English/Hindi — jo bhi likho, summary usi mein milegi
- One task at a time gives best results; big jobs → agent writes `PLAN.md` first
- Long renders run in the background — don't block; QC gate before delivery
- Skill files are editable: tweak playbooks or add scripts anytime, then
  refresh `MANIFEST.json`
