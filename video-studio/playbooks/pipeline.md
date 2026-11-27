# Pipeline Playbook — exact commands for each stage

## Stage 1 — BRIEF
Write `PLAN.md` (non-trivial videos):
```
## Brief
- purpose / audience / platform:
- target duration:
- language:
- tone:
- assets the user already has:
- assets to generate:
```

## Stage 2 — SCRIPT
Write `script.md` in the SKILL.md §3 format. Rules:
- Narration first: every scene has a spoken line (drives timing + subtitles).
- Keep each scene 2–12 s of narration (~30–140 characters).
- `Visual` = a direct image-generation prompt (camera, lighting, composition).
- Put user-supplied images in `images/scene_0N.png` and reference via `Image`.

## Stage 3 — PLAN
```bash
python3 scripts/vs_plan.py script.md --out scene_manifest.json
# optional: --min 2 --max 20 --xfade 0.5 --width 1920 --height 1080 --fps 30
```
Check the printed scene list. Fix any scene whose estimated duration looks wrong
(edit `Duration` in the script) before spending render time.

## Stage 4 — ASSETS
- Generate one image per scene → `images/scene_01.png …` (native `generate_image`,
  prompt = the scene's `Visual` line; keep aspect ratio close to the target).
- Real footage (motion) → see `platforms.md`. Name files `scene_0N.mp4` and
  render them with `vs_render.py` per-scene is for images; for real footage
  clips, place them as the scene `Image` path only if static — for moving
  footage, use `concat_video.py` to assemble clips, then treat the joined
  video as the visual base (override scene video via render workaround below
  or cut footage to scene length with ffmpeg `-t` first).
- If the user supplies photos, keep their aspect: `vs_render.py` scales +
  crops to the manifest resolution automatically.

## Stage 5 — VOICE
```bash
# default: free Microsoft Edge neural voices
python3 scripts/vs_tts.py scene_manifest.json --out-audio narration/ \
    --engine edge --voice en-US-JennyNeural --rate "+0%"

# Hindi / other languages: pick a region voice, e.g.
#   hi-IN-SwaraNeural, es-MX-DaliaNeural, ja-JP-NanamiNeural

# offline fallback (self-test / no network)
python3 scripts/vs_tts.py scene_manifest.json --out-audio narration/ --engine silent

# local TTS CLI (chatterbox/kokoro/espeak), template fills {out} and {text}
python3 scripts/vs_tts.py scene_manifest.json --out-audio narration/ \
    --engine cmd --cmd 'my-tts -o {out} "{text}"'
```
The script rewrites the manifest with real audio durations. If edge-tts
fails (network), fall back to `--engine silent` and note it, or use Arena's
native `generate_speech` and drop the resulting file into `narration/`.

## Stage 6 — RENDER
```bash
# core render (images + narration)
python3 scripts/vs_render.py scene_manifest.json --out video.mp4 --images-dir images/

# with background music (royalty-free only — see platforms.md)
python3 scripts/vs_render.py scene_manifest.json --out video.mp4 \
    --images-dir images/ --music music/track.mp3 --bgm-volume 0.18

# hard cuts instead of crossfades
python3 scripts/vs_render.py scene_manifest.json --out video.mp4 --xfade 0

# keep intermediate clips for debugging
python3 scripts/vs_render.py scene_manifest.json --out video.mp4 --work workdir/
```
What it does: Ken Burns (alternating zoom in/out) → per-scene title card →
chained crossfades → narration acrossfade chain → BGM looped/ducked/faded →
loudnorm I=-14 TP=-1 → H.264 + AAC + faststart.

For long videos (>2 min), render in chunks (split the script into parts),
render each, then `concat_video.py part1.mp4 part2.mp4 --out full.mp4`.

## Stage 7 — QC
```bash
# subtitles first (from the script timings or actual audio)
python3 scripts/vs_qc.py video.mp4 --srt subs.srt --out QC.md
python3 scripts/vs_qc.py video.mp4 --out QC.md   # no subs
```
Gate: decode clean (FAIL = never deliver), loudness within ±1 LU of target,
no silent gaps > 2 s, subtitles in sync. Fix the root cause, re-render.

## Stage 8 — PACKAGE
See `publish.md`. Deliverables: `video.mp4`, `thumb.jpg`, `subs.srt`,
`QC.md`, optional `seo.md`.
