# YouTube Agent Skills — 11 channel skills, integrated

Upstream: [Jakeschincariol/youtube-agent-skill](https://github.com/jakeschincariol/youtube-agent-skill)
(MIT). Integrated into this repo verbatim — skills + their Python tools,
verified working. Nothing publishes anything: these skills write, you upload.

| Skill | What it does | Tools |
|---|---|---|
| `yt-script` | One idea → script. 5 hooks off 21 formulas, scored before you record | `hookscore.py`, `hooks.json` |
| `yt-package` | Title + thumbnail as ONE pairing, linted for truncation/duplication/vagueness | `title.py` |
| `yt-edit` | Transcript → edit decision list: dead air, filler cues, retakes + timecodes | `deadair.py` |
| `yt-comment` | Comment section triaged into 4 piles, replies in your voice, pin pick | — |
| `yt-plan` | A week of uploads sized to your real capacity (anchor + cheap + 3 Shorts) | — |
| `yt-viral` | Niche research ranked by multiple over each channel's own median | `swipe.py` |
| `yt-retention` | Studio retention export → exact drop-off seconds + what to change | `retention.py` |
| `yt-chapters` | Transcript → chapters validated against YouTube's own rules | `chapters.py` |
| `yt-seo` | Description, tags, search-facing text aimed at the real query | — |
| `yt-shorts` | Find the Shorts hiding inside a long video | — |
| `yt-audit` | Channel audit that ends in ONE fix, not twenty | — |

## Voice profile (all skills read it)

`templates/voice.md` upstream → copy to `~/.claude/youtube/voice.md` or keep
one in the workspace and tell the agent where it is. Every skill writes in
the creator's voice from it.

## Quick use (from repo root)

```bash
python3 youtube-skills/yt-script/hookscore.py --hook "your hook line"
python3 youtube-skills/yt-package/title.py --title "..." --thumb "..."
python3 youtube-skills/yt-chapters/chapters.py transcript.srt --target 8
python3 youtube-skills/yt-retention/retention.py retention.csv
```

On Arena: route YouTube requests to these skills via super-skill's router
(`youtube, upload, video seo, srt, chapters…` → `playbooks/video-youtube.md`,
which now points here) and video-studio's `playbooks/publish.md`.
