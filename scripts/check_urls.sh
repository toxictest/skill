#!/usr/bin/env bash
# Verify HTTP status of URLs before citing them — super-skill research-web playbook.
# Usage:  check_urls.sh URL [URL...]
#         check_urls.sh -f urls.txt        (one URL per line, # comments allowed)
# Exit:   0 = all OK (2xx/3xx), 1 = any failed.
set -u
fail=0

check() {
  local url="$1"
  [ -z "$url" ] && return
  case "$url" in \#*) return ;; esac
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 \
         -A "Mozilla/5.0 (super-skill link check)" "$url" 2>/dev/null || true)
  if [ -z "$code" ] || [ "$code" = "000" ]; then code="ERR"; fi
  if [[ "$code" =~ ^[23] ]]; then
    printf 'OK   %s  %s\n' "$code" "$url"
  else
    printf 'FAIL %s  %s\n' "$code" "$url"
    fail=1
  fi
}

if [ "${1:-}" = "-f" ]; then
  [ -f "${2:-}" ] || { echo "file not found: ${2:-}" >&2; exit 1; }
  while IFS= read -r line; do check "$(echo "$line" | xargs)"; done < "$2"
elif [ $# -ge 1 ]; then
  for u in "$@"; do check "$u"; done
else
  echo "Usage: check_urls.sh URL [URL...]  |  check_urls.sh -f file" >&2
  exit 1
fi
exit $fail
