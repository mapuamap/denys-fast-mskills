#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MODE="${1:-startup}"

printf '\n<m_code-context mode="%s">\n' "$MODE"

if [ -f "$ROOT/.claude/AI_INVARIANTS.md" ]; then
  cat "$ROOT/.claude/AI_INVARIANTS.md"
fi

if [ -f "$ROOT/docs/ai/HANDOFF.md" ]; then
  printf '\n## Current handoff\n\n'
  # Keep injected handoff bounded. Claude can read the full file if needed.
  sed -n '1,180p' "$ROOT/docs/ai/HANDOFF.md"
fi

printf '\n</m_code-context>\n'
