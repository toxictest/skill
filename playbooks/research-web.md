# Playbook: Research & Web Browsing

**Triggers**: research, find out, compare, "latest", news, scrape, crawl,
sources, literature, "web se dhoond".

## Workflow

1. **Frame the question** — restate as 1–3 answerable sub-questions with a
   target output (summary, comparison table, citation list).
2. **Search** — `web_search` with `depth: 2` (use `3` for deep dives).
   Query in the language that yields best results (English for tech/legal,
   Hinglish fine for local topics). Run 2–4 varied queries, not one.
3. **Fetch the primary sources** — `fetch_page` on the 3–8 best results.
   Prefer official docs, primary research, reputable outlets over SEO filler.
   GitHub repos: read README + repo root (see ANALYSIS.md for known repos).
4. **Cross-check** — any surprising/number-heavy claim needs a 2nd source.
   Conflicting sources → present both with attribution.
5. **Synthesize** — answer first, then evidence. Every factual claim from
   the web carries `[id](url)` citation. No citation, no claim.
6. **Link-check before delivery** — run `scripts/check_urls.sh URL1 URL2 …`
   (or `-f urls.txt`); swap out any FAILing citation or disclose it.
7. **Harvest more sources** — `scripts/link_extract.py URL --keyword X`
   pulls all anchor links from a page filtered by keyword (seed further
   fetches from the results).

## Output format

- Direct answer (2–6 lines) → structured detail (bullets/table) →
  **Sources** list with `[id](url)`.
- Comparison tasks → markdown table (option + `show_items` if the user
  should pick visually; only use URLs actually fetched, never guessed).

## Tool escalation (install only if needed)

| Need | Tool | Install hint |
|---|---|---|
| Bulk site crawling | crawl4ai | `pip install crawl4ai` |
| JS-heavy scraping | browser-use / Stagehand | needs local browser |
| Deep multi-source reports | gpt-researcher | `pip install gpt-researcher` |
| Markdown-ready crawl API | firecrawl | API key required |

## Pitfalls

- Google Drive/view links (auth+JS) → fail to fetch; ask for a direct
  download or `export=download` URL.
- Never fabricate prices, stats, or image URLs; `show_items` only with
  fetched data.
- Dated knowledge → always verify current facts via search (today's date
  is in system context).
- Paywalled/403 pages → summarize what's available, say the limit.
