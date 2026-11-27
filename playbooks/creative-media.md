# Playbook: Image, Video & Creative Media

**Triggers**: image, logo, poster, thumbnail, banner, illustration, video,
voice, audio, narration, design, "bana do".

## Image generation (native-first)

1. Write ONE precise prompt per image (subject, style, lighting, composition,
   text-free unless requested) → `generate_image`.
2. **Options rule**: if the user asked for variations/options/comparison, or
   is unsure how it should look → exactly one `generate_image` call with
   `offer_options: true` (produces distinct candidates). If they asked for
   one specific picture, or asked NOT to see options → plain call.
   Never build grids/collages inside a single image.
3. Edits/restyle of an existing image → pass its path in `images`.
4. Save under `/home/user/`, `present_file`, iterate on feedback
   ("darker", "more minimal") with a follow-up call on the same path.

## Voice & audio (native-first)

1. `add_voice` first (register pair; content ≈ 15 sec preview). For multiple
   speakers, register ALL voices in one response, then generate.
2. `generate_speech` with the chosen `voice_id`; split long text at sentence
   boundaries and issue parallel calls; ≤10 clips per turn.
3. **Honesty**: output is spoken word — it cannot sing; warn before any
   song request. Language must match the audition language (register a
   language-appropriate voice otherwise).

## Video (working pipeline 🎬)

> **Full pipeline + YouTube publishing** → `playbooks/video-youtube.md`
> (problem→solution log, SEO recipe, concat/SRT/SEO scripts). This section
> = quick in-Arena basics.

**Bundled renderer** (tested): `scripts/make_video.py` —
```
# images → mp4 (H.264 via bundled static ffmpeg):
python3 scripts/make_video.py frames/*.png --duration 2 --fps 24 --out clip.mp4
# with narration:
python3 scripts/make_video.py frames/*.png --audio narration.wav --out clip.mp4
# self-test:  python3 scripts/make_video.py --demo --out demo.mp4
```

**Full AI-video pipeline (in Arena)**:
1. Script → `add_voice` + `generate_speech` (narration WAV/MP3)
2. Frames/art → `generate_image` (one per scene) or PIL programmatic slides
3. Stitch → `scripts/make_video.py` (+ `--audio` to mux)
4. Native tools have **no text-to-video models** — say so; offer below options.

**External skills (verified, Batch 5)**:
- #87 `Felo-Inc/agent-video-skills` — **23 MIT skills**: generate, edit,
  subtitles, shorts, thumbnails, motion graphics — pick-and-mix.
- #89 `AutoVideo-Agent` — `pip install autovideo-agent` — Markdown →
  storyboard → FFmpeg MP4 + QA, **no API key** (local-first).
- #88 `openfilm` (9.5K★) — collaborative video agent, heavier local app.
- #90 `super-video-maker-skill` — avatar explainers (HeyGen/Seedance/
  Whisper captions) — needs API keys.
- ⛔ #59 `harry-styles/AI-Video-Generator` — **404, never existed** (SEO
  keyword). Do not chase that link.

## Design assets

- Logos/icons/diagrams → `generate_image` for raster; **inline SVG** for
  crisp logos/diagrams (preview-safe, no network).
- ControlNet (#57) needs GPU + Stable Diffusion — local-machine recommendation
  only, not sandbox.

## Bundled design script

- `scripts/palette.py "#hex" [--svg out.svg]` — derive shades/tints from a
  brand color with **WCAG contrast ratios** (AA/AAA guidance) + optional
  SVG swatch strip. Run it before choosing text/background pairs.

## UI/web design taste (Batch 4)

- **frontend-design** (#80, anthropics official, 277K+ installs): apply its
  taste rules — deliberate color/spacing/motion, clear visual hierarchy,
  concrete do/don'ts. **Never ship generic "AI-slop" UI.**
- **web-design-guidelines** patterns: 100+ rules covering accessibility,
  typography, images, dark mode, UX — check UI deliverables against them
  (contrast, alt text, responsive breakpoints).
- Install on user's machine if they want it persistent:
  `npx skills add anthropics/skills --skill frontend-design`

## Ethics (hard rules)

- **facefusion (#58) face-swap**: only with explicit consent of everyone
  depicted; refuse deepfakes of real people, non-consensual imagery, or
  impersonation of real persons/brands for deception.
- No generated imagery that harasses, sexualizes minors, or spreads
  misinformation as real photos — label AI-generated when context matters.
- Respect trademarks: don't fabricate official-looking docs/logos to deceive.
