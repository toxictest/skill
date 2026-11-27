#!/usr/bin/env python3
"""Build a .docx report from simple markdown — super-skill documents playbook.

Usage:  docx_report.py input.md output.docx [--title "T"]
Supports: #/##/### headings, - bullets, | tables |, plain paragraphs.
Validates with office_validate.py logic after write.
"""
import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", default=None, help="prepend a title heading")
    args = ap.parse_args()

    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
    except ImportError:
        print("python-docx missing — pip install python-docx", file=sys.stderr)
        return 1

    src = Path(args.input)
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 1

    doc = Document()
    if args.title:
        h = doc.add_heading(args.title, level=0)
        for run in h.runs:
            run.font.color.rgb = RGBColor(0x7C, 0x3A, 0xED)

    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if re.match(r"^#{1,6}\s", line):
            level = min(len(line) - len(line.lstrip("#")), 4) or 1
            doc.add_heading(line.lstrip("#").strip(), level=min(level, 4))
        elif re.match(r"^[-*]\s+", line):
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                doc.add_paragraph(lines[i].lstrip("-* ").strip(), style="List Bullet")
                i += 1
            continue
        elif re.match(r"^\d+\.\s+", line):
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                doc.add_paragraph(re.sub(r"^\d+\.\s+", "", lines[i]).strip(),
                                  style="List Number")
                i += 1
            continue
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in block]
            rows = [r for r in rows[1:] if not all(set(c) <= set(":- ") for c in r)]
            if rows:
                cols = max(len(r) for r in rows)
                table = doc.add_table(rows=1 + len(rows), cols=cols)
                table.style = "Light Grid Accent 1"
                for j, cell in enumerate(rows[0][:cols]):
                    table.rows[0].cells[j].text = cell
                for ri, row in enumerate(rows[1:], start=1):
                    for j in range(cols):
                        table.rows[ri].cells[j].text = row[j] if j < len(row) else ""
            continue
        else:
            para = doc.add_paragraph()
            para.add_run(re.sub(r"\*\*(.+?)\*\*", r"\1", line)).bold = False
        i += 1

    out = Path(args.output)
    if out.suffix.lower() != ".docx":
        out = out.with_suffix(".docx")
    doc.save(out)

    # validate
    import zipfile
    ok = zipfile.is_zipfile(out) and "[Content_Types].xml" in zipfile.ZipFile(out).namelist()
    print(f"wrote {out} ({out.stat().st_size} bytes) — {'VALID OOXML ✅' if ok else 'VALIDATION FAILED ❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
