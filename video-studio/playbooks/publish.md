# Publish Playbook — packaging a finished video

## 1. Deliverables checklist
```
video.mp4   ← QC'd master (H.264, AAC, faststart, -14 LUFS)
thumb.jpg   ← 1280x720 title thumbnail
subs.srt    ← subtitles
QC.md       ← verification report
seo.md      ← optional: titles/tags/description (super-skill youtube_seo.py)
```

## 2. Subtitles
```bash
# from narration audio + scene text (super-skill helper)
python3 ../super-skill/scripts/make_srt.py --audio narration/ --text text/ --out subs.srt
# or hand-time from scene durations in scene_manifest.json
```
Verify with `vs_qc.py video.mp4 --srt subs.srt`.

## 3. Thumbnail
```bash
python3 scripts/vs_thumb.py video.mp4 --title "Hook line (<45 chars)" \
    --subtitle "channel name" --out thumb.jpg
```
Keep title big, ≤2 lines, no tiny text. Grab the most representative frame
(`--at` to choose manually).

## 4. YouTube SEO kit (reuse super-skill)
```bash
python3 ../super-skill/scripts/youtube_seo.py "topic" --clips 3 --out seo.md
```
Then merge: pick the strongest title from `seo.md`, keep tags ≤ 10,
write the description with timestamps matching the scenes.

## 5. Platform specs (sanity targets)
| Platform | Resolution | Max length (typical free) | Notes |
|---|---|---|---|
| YouTube | 1920x1080 (4K ok) | 12 h (verified accounts) | -14 LUFS normalization; add AI-content disclosure if generated [4](https://aldricresearch.com/best-ai-video-generators-2026) |
| YouTube Shorts / IG Reels | 1080x1920 (9:16) | 60–90 s | Render with `vs_plan.py --width 1080 --height 1920` |
| WhatsApp / Telegram | 1920x1080 | ≤ 16 min (app limits) | H.264 + AAC MP4 plays everywhere |

Re-render with a different aspect ratio by changing `--width/--height` in
`vs_plan.py` and re-running the pipeline — don't crop a 16:9 master to 9:16.

## 6. Final gate
1. `vs_qc.py video.mp4 --srt subs.srt` → no FAIL.
2. Thumbnail opens, title readable at small size.
3. `seo.md` (if requested) has title/tags/description/chapters.
4. `present_file` the MP4; mention supporting files by name in chat.
