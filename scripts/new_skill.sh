#!/usr/bin/env bash
# Scaffold a new Agent Skill folder (agentskills.io standard) — super-skill meta tool.
# Usage:  new_skill.sh <skill-name> ["One-line description of when to use it"]
# Rules:  lowercase letters/digits/hyphens; cannot contain "claude" or "anthropic".
set -euo pipefail

name="${1:-}"
desc="${2:-Replace with description of the skill and when the agent should use it.}"

if [ -z "$name" ]; then
  echo "Usage: new_skill.sh <skill-name> [\"description\"]" >&2
  exit 1
fi
if ! [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "invalid name '$name': use lowercase letters, digits, hyphens only" >&2
  exit 1
fi
case "$name" in
  *claude*|*anthropic*)
    echo "invalid name '$name': cannot contain reserved words 'claude' or 'anthropic'" >&2
    exit 1;;
esac
if [ -e "$name" ]; then
  echo "already exists: $name/" >&2
  exit 1
fi

mkdir -p "$name/references" "$name/scripts"
cat > "$name/SKILL.md" <<EOF
---
name: $name
description: $desc
---

# $name

## When to use
<!-- activation triggers -->

## Instructions
<!-- step-by-step workflow -->

## References
- references/  — deep-dive docs loaded on demand
- scripts/     — runnable helpers (stdlib-first, no install)
EOF

echo "created $name/"
echo "  $name/SKILL.md"
echo "  $name/references/"
echo "  $name/scripts/"
echo "next: edit description (<=1024 chars) and add instructions."
