#!/usr/bin/env python3
"""Validate Office files (.docx/.xlsx/.pptx) before delivery — super-skill documents playbook.

Usage:  office_validate.py FILE [FILE...]
Exit:   0 = all valid, 1 = at least one invalid.
Checks: OOXML zip integrity, required parts, legacy-format rejection,
        deep parse via python-docx / openpyxl / python-pptx when available.
"""
import sys
import zipfile
from pathlib import Path

LEGACY = {".doc", ".ppt", ".xls"}
ALLOWED = {".docx", ".xlsx", ".pptx"}
REQUIRED = {
    ".docx": "word/document.xml",
    ".xlsx": "xl/workbook.xml",
    ".pptx": "ppt/presentation.xml",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"file not found: {path}"]
    if path.suffix.lower() in LEGACY:
        return [f"legacy format {path.suffix} rejected — produce modern OOXML instead"]
    if path.suffix.lower() not in ALLOWED:
        return [f"unsupported extension: {path.suffix} (expected .docx/.xlsx/.pptx)"]
    if not zipfile.is_zipfile(path):
        return [f"not a valid OOXML zip: {path}"]

    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "[Content_Types].xml" not in names:
            errors.append("missing [Content_Types].xml")
        corrupt = z.testzip()
        if corrupt:
            errors.append(f"corrupt zip member: {corrupt}")
        req = REQUIRED[path.suffix.lower()]
        if req not in names:
            errors.append(f"missing required part: {req}")

    if not errors:  # deep parse only when structure is sound
        try:
            if path.suffix.lower() == ".docx":
                import docx
                d = docx.Document(str(path))
                print(f"  parse OK: {len(d.paragraphs)} paragraphs, {len(d.tables)} tables")
            elif path.suffix.lower() == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(str(path), read_only=True)
                print(f"  parse OK: sheets={wb.sheetnames}")
                wb.close()
            elif path.suffix.lower() == ".pptx":
                try:
                    from pptx import Presentation
                    pr = Presentation(str(path))
                    print(f"  parse OK: {len(pr.slides)} slides")
                except ImportError:
                    print("  parse: python-pptx not installed — zip-level checks passed")
        except Exception as exc:  # noqa: BLE001 — any parse failure = invalid
            errors.append(f"parse failed: {exc}")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    failed = False
    for arg in sys.argv[1:]:
        path = Path(arg)
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
