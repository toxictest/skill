---
name: video-studio
description: God-level video creation skill — turns any video request into a REAL, watchable video: Markdown script → scene plan → AI images / generated footage → voiceover → edited MP4 (Ken Burns motion, crossfades, titles, mixed music, loudness-normalized) → QC → thumbnail + YouTube package. Use for ANY video request: shorts, explainer, promo, launch video, slideshow with narration, avatar-free talking-head alternatives. Auto-routes and runs end to end; no API key needed by default (bundled ffmpeg + free TTS).
---

# Video Studio — real video, end to end

You have been given this skill to make videos. Follow it exactly. The output
must be a **real, playable MP4** — not a description of how to make one.

## 0. What this skill is

A self-contained video production pipeline, distilled from the current
(2026) state of AI video tooling: hosted generation models (Sora 2, Veo 3,
Kling 3, Runway Gen-4), open-weight models you can self-host (Wan 2.2,
HunyuanVideo 1.5, LTX-Video), best-in-class free TTS (edge-tts, Chatterbox,
Kokoro), and the AutoVideo-Agent / OpenFilm pipeline pattern
(Script → Storyboard → Manifest → Media → Timeline → FFmpeg → QA → MP4).

```
video-studio/
├── SKILL.md           ← you are here (router + pipeline)
├── playbooks/
│   ├── pipeline.md    ← the 7-stage workflow with exact commands
│   ├── platforms.md   ← where footage / voice / music come from (2026 research)
│   └── publish.md     ← YouTube + social packaging
└── scripts/
    ├── vs_plan.py     ← Markdown script → scene_manifest.json (timings)
    ├── vs_tts.py      ← narration: edge-tts / silent / custom CLI → real durations
    ├── vs_render.py   ← manifest → real MP4 (Ken Burns, xfade, titles, BGM, loudnorm)
    ├── vs_qc.py       ← decode + loudness + silence + subtitle gate → QC.md
    ├── vs_thumb.py    ← 1280x720 thumbnail with title card
    └── vs_selftest.py ← hermetic end-to-end pipeline test (run before shipping)
```

## 1. Intake — AUTO-MODE (always on)

Any request that asks for a video — "video banao", "shorts", "explainer",
"promo video", "launch video" — routes here. Do NOT ask the user to invoke
the skill. Workflow:

1. **Clarify in ONE round max** (`ask_user`, ≤4 questions) only if a missing
   detail changes the deliverable materially: purpose/platform, duration,
   language, tone, assets the user already has. Otherwise state assumptions
   and proceed.
2. **Run `vs_selftest.py` once** if you changed scripts (package must be healthy).
3. **Brief → Script → render**, per §2. Announce the plan in one line,
   then execute.

## 2. The pipeline (every video)

```
BRIEF → SCRIPT → PLAN → ASSETS → VOICE → RENDER → QC → PACKAGE
```

**Stage 1 — BRIEF**: one-line intent: who watches, where (YouTube/IG/WhatsApp),
how long, which language. Write `PLAN.md` for non-trivial videos.

**Stage 2 — SCRIPT**: write `script.md` in the scene format (§3). Narration
is the backbone of every scene — timing, subtitles and flow hang off it.

**Stage 3 — PLAN**:
```bash
python3 scripts/vs_plan.py script.md --out scene_manifest.json
```
Estimates scene durations (chars/sec), clamped to sane bounds.

**Stage 4 — ASSETS**: per scene, get a visual (see `playbooks/platforms.md`):
- default/native: `generate_image` with the scene's Visual line as prompt
  (or user-supplied photo/footage) → `images/scene_01.png`
- real motion footage: hosted APIs (Sora 2 / Veo 3 / Kling 3 / Runway Gen-4)
  or local ComfyUI (Wan 2.2 etc.) — see platforms.md for what to pick
- placeholder cards are generated automatically only as a last resort

**Stage 5 — VOICE** (narration is mandatory unless user says silent):
```bash
python3 scripts/vs_tts.py scene_manifest.json --out-audio narration/ --engine edge
```
`--voice` picks the persona (e.g. `en-US-JennyNeural`, `hi-IN-SwaraNeural`);
`--engine silent` for offline/self-test; `--engine cmd --cmd '...'` for local
TTS (Chatterbox, Kokoro, espeak). On Arena, `add_voice` + `generate_speech`
is the native alternative — then point the scene's `audio` at the file.

**Stage 6 — RENDER** (makes the REAL video):
```bash
python3 scripts/vs_render.py scene_manifest.json --out video.mp4 \
    --images-dir images/ [--music track.mp3] [--xfade 0.5]
```
Ken Burns motion + crossfades + on-screen titles + narration + ducked BGM +
loudnorm to **-14 LUFS / -1 dBTP** (YouTube standard). Audio-driven scene
timings, so the video matches the voiceover.

**Stage 7 — QC (non-negotiable gate)**:
```bash
python3 scripts/vs_qc.py video.mp4 --srt subs.srt --out QC.md
```
Decode-clean, loudness, silence and subtitle checks must pass before delivery.
Never present a video you have not run through QC.

**Stage 8 — PACKAGE** (`playbooks/publish.md`): thumbnail + subtitles +
SEO kit. Reuse super-skill helpers: `make_srt.py`, `youtube_seo.py`,
`concat_video.py` (joining clips), `check_urls.sh`.

## 3. Script format (scene_manifest input)

```markdown
# Video: Sunrise in the City

## Scene 1 — Hook
| Visual    | Cinematic sunrise over a calm city skyline, timelapse clouds |
| Narration | Welcome back. Today we are chasing the sunrise over the city. |
| Title     | Sunrise in the City |
| Music     | ambient uplifting |

## Scene 2 — The climb
| Visual    | Drone shot rising over rooftops toward the brightening sky |
| Narration | From the rooftops, the city wakes up one light at a time. |
| Image     | images/scene_02.png |
```
Keys: `Visual` (required), `Narration` (required — drives timing),
`Title` (on-screen text), `Image` (path), `Music` (mood note),
`Duration` (seconds; default `auto` from narration length).

## 4. Tool policy

- **Bundled scripts first** (stdlib + light deps, tested): vs_plan / vs_tts /
  vs_render / vs_qc / vs_thumb, plus super-skill's `make_srt.py`,
  `youtube_seo.py`, `concat_video.py`, `make_video.py`.
- **Native tools**: `generate_image` (scene art), `add_voice` +
  `generate_speech` (narration), `start_process` (long renders),
  `present_file` (delivery).
- **Deps**: `pip install -r ../requirements.txt` (pillow, imageio-ffmpeg,
  edge-tts). Everything else degrades gracefully with clear messages.
- **Long renders**: use `start_process` for big jobs; renders are CPU-heavy.

## 5. Quality bar (non-negotiable)

- **Real video only**: the deliverable is an MP4 you QC'd, never a plan.
- **Evidence-grounded sourcing**: state exactly where each asset came from
  (generated / user-supplied / API / stock); never invent a source.
- **Audio discipline**: narration-driven timing; BGM ducked under voice;
  final loudness near -14 LUFS (platforms normalize to it).
- **QC gate**: `vs_qc.py` PASS (or WARN with reasons stated) before delivery.
- **Honest reporting**: if TTS fell back to silent, a clip is a placeholder,
  or an API was unavailable — say it plainly in the summary.

## 6. Safety guardrails (hard rules)

- **Voice**: no cloning a real person's voice without their consent.
  Prefer platform-native voices or clearly licensed models (Chatterbox
  embeds a provenance watermark; note it when used).
- **Music**: only royalty-free / licensed tracks (YouTube Audio Library,
  Freesound, Pixabay, or user-licensed). No copyrighted tracks.
- **Footage**: AI-generated or user-owned assets only; no scraping
  watermarked/private content.
- **Disclosure**: when platforms require AI-content labels, say so.
- **Scope**: if the request is deepfake/misleading of real people — decline,
  offer the legitimate alternative (original footage + narration).

## 7. Output contract

Every task ends with:
1. Main artifact presented (`present_file`): the MP4 (+ thumb, SRT, QC.md,
   SEO kit as supporting files, named in chat).
2. Short chat summary in the user's language: what was made, scene list,
   where each asset came from, assumptions.
3. Verification evidence: QC.md summary line + render output line.
4. Optional next steps (max 3, concrete).

## Arena mode (Arena.ai Agent Mode)

This skill is Arena-native: the agent auto-routes to this SKILL.md, uses
native tools (`generate_image`, `add_voice` + `generate_speech`,
`start_process` for long renders) and delivers via `present_file`. Long
renders run as background processes — never block the turn. See
`../USAGE-ARENA.md` for the full Arena walkthrough.
