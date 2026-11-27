# Playbook: video-youtube.md — Video Production + YouTube Publishing

**Load when:** youtube, upload, seo, srt, subtitles, chapters, end screen,
reels/shorts publishing, channel growth. (Making a video = also see
creative-media.md §Video; this file = full pipeline + publishing.)

## 1. End-to-end pipeline (proven on Arena — "Linux Basics" episode)

```
script (per-scene narration text)
  → slides: PIL 1280x720 (English text OK; Hindi voiceover explains)
  → narration: add_voice (audition once) → generate_speech per scene → .wav
  → clips: scripts/make_video.py slide.png --audio scene.wav --duration (wav+0.6) --out scene.mp4
  → join: scripts/concat_video.py --glob 'clips/*.mp4' --out final.mp4
  → subtitles: scripts/make_srt.py --audio audio/ --text text/ --out subs.srt
  → thumbnail: PIL + Noto font (1280x720, big text, terminal motif)
  → seo: scripts/youtube_seo.py "Topic" --duration M:SS --clips clips/ --out seo.md
  → upload: title/desc/tags/chapters + schedule 7-9 PM IST Tue-Thu/Sun
```

## 2. Problem → Solution log (encountered & fixed — don't rediscover)

| # | Problem on Arena | Solution (now bundled/known) |
|---|---|---|
| 1 | No system fonts (`/usr/share/fonts` empty of TTFs) | DejaVu TTFs ship inside **matplotlib**: `Path(matplotlib.__file__)/mpl-data/fonts/ttf` (also `/usr/share/fonts/truetype/dejavu/`) |
| 2 | Hindi/Devanagari renders as tofu boxes | Download **Noto Sans Devanagari** (OFL): `raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf`. **Verify properly**: render text and count ink pixels (`>500`) — `font.getmask().getbbox()` gives false positives (tofu box also has bbox) |
| 3 | No system ffmpeg | `pip install imageio imageio-ffmpeg` → `imageio_ffmpeg.get_ffmpeg_exe()` = static binary (encode, concat, probe, decode-check) |
| 4 | `generate_speech` limit = **10 clips/turn** | Plan scene batches across turns; do slides + other work while waiting; never burn turns on failed parallel calls |
| 5 | `make_video.py --audio` uses `-shortest` → **clip length = audio length** (pad ignored) | SRT scene boundaries = raw WAV durations (`--pad 0`); only pass `--duration wav+0.6` when you want hold-time after speech |
| 6 | Joining clips: concat needs identical params | `scripts/concat_video.py`: concat demuxer + `-c copy` + `+faststart`, auto **fallback re-encode**, then full decode-check (stderr empty = clean) |
| 7 | SRT timing hand-math is error-prone | `scripts/make_srt.py`: WAV duration per scene + character-proportional chunk allocation; validates non-overlapping cues |
| 8 | YouTube chapters need ≥10s each, first = 0:00 | `youtube_seo.py --clips` probes cumulative starts and flags `<10s` violations |
| 9 | Devanagari TTS pronunciation | Use `language: "hi"` + **Devanagari script** (not romanized Hinglish — TTS mispronounces) |

## 3. YouTube SEO recipe (what ranked the sample)

- **Title ≤65 chars**, primary keyword in first 40, `|` separators, year + number
  ("4 Min", "2026") for CTR. Keep 3-5 variants for A/B.
- **Description**: first 2 lines keyword-dense (visible pre-"show more"),
  then bullet content map, chapters, hashtags, subscribe CTA.
- **Tags**: 15-25 phrase variants, ≤500 chars (hindi/eng mix for Indian audience).
- **Hashtags**: exactly 3 above title, 8-10 in description.
- **Chapters**: ≥10s, 0:00 start, keyword-y labels (searchable queries).
- **Pinned comment** = question/quiz (replies = engagement velocity).
- **Boost**: upload 7-9 PM IST (Tue-Thu/Sun); Shorts clip 30s from the
  juiciest scene with full-video link; reply to every comment first hour;
  next episode within 7 days (series momentum); Community post poll.
- Settings: Category **Education**, upload `.srt` (Hindi), end screen =
  subscribe + next episode, card mid-video → playlist.

## 4. Quality gate before "upload" claim

- [ ] Full decode check clean (`ffmpeg -v error -i final.mp4 -f null -`)
- [ ] Duration matches chapters; SRT last cue ≤ video length
- [ ] Thumbnail: 1280x720, ≤5 words readable on mobile, Hindi renders (ink test)
- [ ] `youtube_seo.py` output pasted (title char count ≤65)
- [ ] File sizes sane (<200MB target for 1080p shorts-length content)

## 5. Bundled scripts (all tested — see SKILL.md §4)

| Script | Job |
|---|---|
| `make_video.py` | images + narration → H.264 MP4 |
| `concat_video.py` | join MP4s (copy → re-encode fallback) |
| `make_srt.py` | WAV+TXT scenes → timed SRT |
| `youtube_seo.py` | topic → titles/tags/desc/chapters kit |
| `palette.py`, `chart.py`, `html_template.py` | supporting assets |

Voice: `add_voice` (once) → `generate_speech` (10/turn, batch plan).
