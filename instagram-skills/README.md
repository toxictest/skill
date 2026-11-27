# Instagram Skills — caption, Reels, grid

A focused Instagram pack in the same format as the integrated YouTube pack
(`youtube-skills/`): three skills, each with a tested Python tool. Nothing
posts anything — the skills write, the user posts.

| Skill | What it does | Tool |
|---|---|---|
| `ig-caption` | Hook-first caption variants + focused hashtag block, linted for the 2200-char limit, hook-fold length, and shadowban-risk tags | `ig_caption.py` |
| `ig-reels` | Validates a Reel (9:16, duration, audio, decode), extracts a cover with IG UI safe zones marked, writes a publish plan | `ig_reels.py` |
| `ig-grid` | Plans a cohesive feed grid / carousel: thematic coherence check, snake/swipe slot ordering, per-slot hook plan | `ig_grid.py` |

## Quick use (from repo root)

```bash
python3 instagram-skills/ig-caption/ig_caption.py --topic "sunrise city walk" --audience "travel lovers" --out caption.md
python3 instagram-skills/ig-reels/ig_reels.py --video reel.mp4 --title "Sunrise in 4K" --out cover.jpg
python3 instagram-skills/ig-grid/ig_grid.py --idea "sunrise city walk" --idea "rooftop coffee" --layout 3 --out grid_plan.md
python3 instagram-skills/ig_selftest.py   # hermetic pack test
```

Compose with `video-studio/` (render the 9:16 Reel) and `youtube-skills/`
(voice profile convention for consistent creator tone).
