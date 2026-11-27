#!/usr/bin/env bash
# LibreOffice headless conversion wrapper — super-skill documents playbook.
# Usage:  soffice_convert.sh INPUT [TARGET_FMT] [OUT_DIR]
#         soffice_convert.sh report.docx pdf
#         soffice_convert.sh data.xlsx csv ./converted
set -euo pipefail

in="${1:-}"
fmt="${2:-pdf}"
out_dir="${3:-.}"

if [ -z "$in" ]; then
  echo "Usage: soffice_convert.sh INPUT [TARGET_FMT] [OUT_DIR]" >&2
  exit 1
fi
if [ ! -f "$in" ]; then
  echo "not found: $in" >&2
  exit 1
fi

if ! command -v soffice >/dev/null 2>&1; then
  cat >&2 <<'MSG'
soffice not found — LibreOffice is not installed in this sandbox.
Install options:
  Debian/Ubuntu:  sudo apt-get install -y libreoffice-core
  Fallback:       pip install markitdown   (office -> markdown)
                  python-docx / openpyxl / python-pptx for programmatic writes
MSG
  exit 127
fi

mkdir -p "$out_dir"
soffice --headless --convert-to "$fmt" --outdir "$out_dir" "$in"
echo "converted -> $out_dir/$(basename "${in%.*}").$fmt"
