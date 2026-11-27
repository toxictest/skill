---
name: ig-grid
description: Plan a cohesive Instagram feed grid or carousel — check thematic coherence across post ideas, order the slots for the scroll/swipe journey, and write a per-slot caption plan. Use for "plan my feed", "grid ideas", "carousel post", "my next 5 posts", or any request to structure multiple Instagram posts into one series.
---

# ig-grid

A grid is a series, not a pile. The viewer reads the 3×3 (or carousel) as
one story before deciding to follow — cohesion is the whole game.

## Workflow

1. **Collect the ideas** (from the user or generated): 3–5 posts, each a
   clear visual + topic.
2. **Plan**:
   ```bash
   python3 ig_grid.py --idea "<post 1>" --idea "<post 2>" --idea "<post 3>" \
       --layout 3 --series-name "<series name>" --out grid_plan.md
   ```
   `--layout` is `3` / `4` / `5` (grid, snake-ordered for the scroll
   journey) or `carousel` (swipe order, hook first).
3. **Read the verdict**: cohesion ≥ 60% means the set reads as one series;
   weak links get named. If cohesion is loose, either center the set on the
   shared keywords or split it into two series.
4. **Deliver**: `grid_plan.md` + per-slot hooks; then pair with
   `ig-caption` for full captions and `ig-reels` if any slot is a Reel.

## Rules

- One series name + consistent cover style across slots — that is what
  makes the grid recognizable at a glance.
- Carousels: slide 1 is the hook frame (must make sense as a standalone
  cover), last slide carries the CTA/save prompt.
- Alt text on every post — accessibility first, reach second.
- If the user gives no ideas, draft 3–5 from their niche first, then run
  the planner — never deliver an empty grid.
