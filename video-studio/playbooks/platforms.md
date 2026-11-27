# Platforms Playbook — where footage, voice and music come from (2026 research)

Research date: 2026-11-27. Every claim below carries a citation. Pick the
**simplest option that meets the brief** — default to generated stills +
narration; add generated motion or stock footage when the video needs it.

## 1. Motion footage — hosted AI generation (API / web)

The 2026 leaders are all at roughly the same quality tier; they differ in
strengths and cost:

| Model | Maker | Strength | Notes |
|---|---|---|---|
| Sora 2 | OpenAI | Cinematic quality, prompt adherence, multi-shot stories | ~60 s clips, 1080p, API available, ~$0.05/s credits [1](https://admix.software/blog/best-ai-video-generators-2026) [3](https://www.aitrove.ai/blog/best-ai-video-generators-2026) |
| Veo 3 / 3.1 | Google | Fastest + cheapest; **native synced audio** (dialogue/Foley/ambient) | 4K, up to 120 s, ~$0.02/s, API via Vertex AI [1](https://admix.software/blog/best-ai-video-generators-2026) [2](https://www.toolcenter.ai/en/articles/ai-video-generation-tools-2026) |
| Kling 3 / 2.6 | Kuaishou | Best realistic **human motion**, best quality-to-cost | ~$0.03/s, 1080p, web + API [1](https://admix.software/blog/best-ai-video-generators-2026) [4](https://aldricresearch.com/best-ai-video-generators-2026) |
| Runway Gen-4 | Runway | Best **editing/camera control** (motion brush, keyframes) | $12–76/mo plans, editing-first workflows [1](https://admix.software/blog/best-ai-video-generators-2026) [5](https://happycapyguide.com/blog/best-ai-video-generation-tools-2026) |

Benchmark detail: a 1,800-clip evaluation scored Sora 2 highest overall
(9.2/10) on temporal coherence and native audio; a finished 10 s clip costs
~$0.40 (Veo 3/Kling) to >$2.00 (Sora 2 at max quality) [4](https://aldricresearch.com/best-ai-video-generators-2026).

**When to use**: the brief needs real motion (product reveal, narrative,
human presence). Cost scales with runtime — keep AI-generated motion to
short hero shots and cover the rest with images + Ken Burns.

## 2. Motion footage — self-hosted open-weight models (free, your GPU)

All Apache-2.0 (commercially clean) unless noted; run via ComfyUI
[3](https://viralmint.net/blog/run-ai-video-generator-locally/):

| Model | VRAM (min) | Practical output (2026) | Notes |
|---|---|---|---|
| Wan 2.2 (Alibaba) | 8 GB (1.3B) / 24 GB (TI2V-5B) / 80 GB (A14B) | ~5 s, 720p, 24 fps | Strong T2V **and** I2V, multilingual prompts; the practical self-host default [1](https://www.sevenlabs.site/blogs/best-open-source-video-generation-models-2026) [3](https://www.ssdnodes.com/learn/self-hosted-ai-video-generator) |
| HunyuanVideo (Tencent) | 45 GB (13B) / **14 GB** (1.5 with offloading) | 480p–720p | Cinematic motion; fine-tune on your own footage under the community license [2](https://wink.ai/blog/text-to-video-ai-models) [3](https://viralmint.net/blog/run-ai-video-generation-locally/) |
| LTX-Video (Lightricks) | 16 GB | up to 20 s incl. audio, 4K/50 fps (LTX-2 line) | Speed/real-time workflows [1](https://www.sevenlabs.site/blogs/best-open-source-video-generation-models-2026) [5](https://www.ssdnodes.com/learn/self-hosted-ai-video-generator) |
| CogVideoX (THUDM) | 5–10 GB | 720×480–1360×768, 6–10 s | Parameterized/controllable output [1](https://www.sevenlabs.site/blogs/best-open-source-video-generation-models-2026) [3](https://viralmint.net/blog/run-ai-video-generation-locally/) |

**When to use**: repeated production with no per-clip costs. Expect ~5 s
units at 720p on consumer GPUs today [5](https://www.ssdnodes.com/learn/self-hosted-ai-video-generator).

## 3. Ready-made agent pipelines (optional)

- **OpenFilm** — open-source AI video agent; `npx skills add openfilm/openfilm`,
  needs Node 22.2+ + ffmpeg; renders MP4 via ffmpeg with a loudness target
  (`--loudness=-14`). Good when you want an interactive editor around the render [4](https://github.com/openfilm/openfilm).
- **AutoVideo-Agent** — local-first Markdown→storyboard→manifest→FFmpeg→QA→MP4
  pipeline with pluggable media/TTS providers; v0.1 uses deterministic
  placeholder assets (no AI generation) — our `vs_*` scripts already cover
  the same pipeline with real assets [1](https://skillsllm.com/skill/autovideo-agent).

## 4. Voice / narration (TTS)

| Option | Cost | Notes |
|---|---|---|
| **edge-tts** (bundled `vs_tts.py --engine edge`) | free, no key | Microsoft neural voices, many languages/region accents — default choice |
| **Chatterbox** (local) | free, MIT | Reportedly beat ElevenLabs in blind tests (63.8% preference); zero-shot cloning from ~5 s; embeds a PerTh provenance watermark — disclose when used [2](https://nerdynav.com/open-source-ai-voice/) [3](https://runfreetools.com/blog/best-free-ai-text-to-speech-2026) |
| **Kokoro-82M** (local) | free, Apache 2.0 | 82M params, runs on CPU, ~54 voices — fastest local narration [1](https://localaimaster.com/blog/best-local-tts-models) [5](https://reviewnexa.com/ai-text-to-speech-tools/) |
| Arena native `add_voice` + `generate_speech` | platform | Best when working inside Arena; voice registered per session |

Voice cloning of real people requires their consent — always.

## 5. Music & sound effects

- **Royalty-free only**: YouTube Audio Library, Freesound (CC-licensed
  subset), Pixabay Music, or user-licensed tracks. Never use copyrighted
  songs in deliverables.
- Music is mixed **ducked** under narration (`--bgm-volume ~0.15–0.2`),
  faded in/out, and loudness is normalized at the end (-14 LUFS).
- SFX (whoosh, click) can be layered per-scene via ffmpeg `adelay` + `amix`
  if the brief calls for it.

## 6. Decision cheat-sheet

| Brief | Footage | Voice |
|---|---|---|
| Explainer / tutorial | images + Ken Burns (native `generate_image`) | edge-tts or native |
| Promo / launch video | 1–2 hero motion clips (Veo 3 if audio-in-sync needed, Kling for people) + image scenes | edge-tts / Chatterbox |
| Personal/branded with real photos | user photos (no generation needed) | native / edge-tts |
| Self-hosted batch production | Wan 2.2 via ComfyUI | Kokoro/Chatterbox local |
