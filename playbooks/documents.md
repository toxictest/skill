# Playbook: Documents (PDF, Word, Excel, PowerPoint)

**Triggers**: PDF, docx, xlsx, pptx, Word, Excel, PowerPoint, report,
spreadsheet, presentation, convert, OCR, "file banao".

## Rules (hard)

- **Modern formats only**: produce `.docx`/`.xlsx`/`.pptx` — never legacy
  `.doc`/`.ppt` (won't preview; only downloadable).
- Validate before delivery: re-open/parse the generated file (python-docx
  read, `zipfile` integrity, openpyxl load) and confirm content.
- Preview iframe has no network → no CDN fonts/images in Office docs that
  must render offline; embed or use standard fonts.
- Data tables → prefer `.xlsx` or `.csv` (both previewable).

## Recipes

| Task | Approach |
|---|---|
| Validate any office file | **`scripts/office_validate.py FILE...`** (zip + deep parse, rejects legacy .doc/.ppt) |
| Report from markdown | **`scripts/docx_report.py in.md out.docx`** — headings/bullets/tables → valid .docx (auto-validated) |
| Create Word/Excel/PPT | `python-docx` / `openpyxl` / `python-pptx` (all preinstalled here) |
| File → Markdown/text | `markitdown` (`pip install markitdown`) — office/PDF to md |
| PDF → structured | `docling` (`pip install docling`) for tables/layout |
| Scanned image/PDF → text | `PaddleOCR` or `ocrmypdf` (`pip install ocrmypdf`) |
| docx/pptx/xlsx → PDF or vice versa | **`scripts/soffice_convert.sh in.xlsx pdf`** (needs LibreOffice; script prints install hint if missing) |
| Large ingestion pipelines | `unstructured` (RAG use-case; heavier) |

## Workflow

1. Identify source format(s) + target format + audience/purpose.
2. If converting: run the conversion, then **diff-check** content survived
   (page count, headings, tables).
3. If creating: confirm structure requirements (sections, tables, branding)
   — one `ask_user` round if format is unspecified and matters.
4. Generate → validate → `present_file`.
5. Summarize contents + any conversion caveats (e.g. "images flattened").

## Caveats

- ONLYOFFICE DocumentServer (#44) is a full server suite — overkill here.
- OCR quality depends on scan clarity; state confidence on noisy scans.
- Never invent data inside a report — mark placeholders clearly.
