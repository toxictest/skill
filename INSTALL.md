# Install — all skill packs in this repo

**Arena.ai first?** On Arena.ai Agent Mode there is nothing to install:
put this repo in the workspace, and every skill auto-routes from the task
itself (see `USAGE-ARENA.md` for the routing table and tool mapping). The
`.claude/skills/` copies below are only for Claude Code.

Repo layout:

| Path | What |
|---|---|
| `SKILL.md` (root) | **super-skill** — universal auto-router (entry point) |
| `video-studio/` | god-level video creation pipeline (real MP4 output) |
| `youtube-skills/` | 11 YouTube channel skills (upstream: Jakeschincariol/youtube-agent-skill, MIT) |
| `instagram-skills/` | Instagram pack: captions, Reels, grid |
| `.claude/skills/` | **installed copies** (yt-* + ig-*) — ready for Claude Code |
| `.claude/youtube/voice.md` | voice profile template for the yt pack |

## Option A — already installed (this repo)

The `.claude/skills/` directory contains all 14 skills installed. In Claude
Code, open this repo as the working directory and the skills resolve
directly. Or copy the folders to a global location:

```bash
cp -r .claude/skills/* ~/.claude/skills/
cp .claude/youtube/voice.md ~/.claude/youtube/voice.md   # then fill it in
```

Then fill `~/.claude/youtube/voice.md` from the template — every yt skill
writes in the creator's voice from it.

## Option B — as a Claude plugin / marketplace

The upstream YouTube pack ships `.claude-plugin/plugin.json` +
`marketplace.json` (kept in the cloned upstream repo). For the integrated
packs here:

```bash
/plugin marketplace add <this-repo>
# skills resolve from .claude/skills/
```

## Option C — project-local

```bash
git clone <this-repo>
# skills are already at .claude/skills/ — open the repo and use them
```

## Option D — super-skill / video-studio on any agent runtime

These two follow the standard Agent Skills layout (`SKILL.md` + frontmatter).
Copy `SKILL.md` (root), `video-studio/`, `playbooks/` and `scripts/` into the
runtime's skills directory. Optional deps:

```bash
pip install -r requirements.txt
```

## Verify the install

```bash
python3 scripts/selftest.py --fast          # super-skill: 48/48
python3 video-studio/scripts/vs_selftest.py  # video-studio: 6/6
python3 youtube-skills/../instagram-skills/ig_selftest.py  # instagram: 3/3
python3 scripts/make_manifest.py --verify  # integrity
```

Nothing in any pack posts or uploads anything — all skills write files;
publishing is always the user's action.
