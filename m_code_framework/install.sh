#!/usr/bin/env bash
# install.sh — Install the m_code framework payload into the current project.
# Self-locating: copies files relative to this script's own directory, so it
# works regardless of where the plugin is installed. No hardcoded paths.
set -e

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="${1:-$PWD}"

if [ "$DST" = "$HOME" ] || [ "$DST" = "/" ]; then
  echo "ERROR: refusing to install into $DST. cd into a project first (or pass a target path)."
  exit 1
fi

echo "Installing m_code framework"
echo "  from: $SRC"
echo "  into: $DST"
echo ""

mkdir -p "$DST/.claude/rules"
mkdir -p "$DST/.claude/hooks"
mkdir -p "$DST/.claude/state"
mkdir -p "$DST/scripts"
mkdir -p "$DST/docs/ai"

# Rules
cp "$SRC/rules/"*.md "$DST/.claude/rules/"
echo "  + .claude/rules (3)"

# Hooks
cp "$SRC/hooks/"* "$DST/.claude/hooks/"
chmod +x "$DST/.claude/hooks/"*.sh 2>/dev/null || true
echo "  + .claude/hooks ($(ls "$SRC/hooks" | wc -l | tr -d ' '))"

# Invariants
cp "$SRC/AI_INVARIANTS.md" "$DST/.claude/"
echo "  + .claude/AI_INVARIANTS.md"

# Hooks docs
cp "$SRC/README-hooks.md" "$DST/.claude/"
echo "  + .claude/README-hooks.md"

# Verification entry script
cp "$SRC/scripts/ai-check.sh" "$DST/scripts/"
chmod +x "$DST/scripts/ai-check.sh"
echo "  + scripts/ai-check.sh"

# settings.json — never clobber an existing one
if [ -f "$DST/.claude/settings.json" ]; then
  cp "$SRC/settings.json" "$DST/.claude/settings.m_code.example.json"
  echo "  ~ .claude/settings.json exists — wrote settings.m_code.example.json instead (merge manually)"
else
  cp "$SRC/settings.json" "$DST/.claude/settings.json"
  echo "  + .claude/settings.json"
fi
cp "$SRC/settings.strict.example.json" "$DST/.claude/"
echo "  + .claude/settings.strict.example.json"

# state marker + gitignore
touch "$DST/.claude/state/.gitkeep"
if [ -f "$DST/.gitignore" ]; then
  grep -q '.claude/state' "$DST/.gitignore" 2>/dev/null || {
    echo '.claude/state/' >> "$DST/.gitignore"
    echo "  + .gitignore updated (.claude/state/)"
  }
fi

echo ""
echo "m_code framework installed."
echo "Next: /m_code_init_project to tailor rules + CLAUDE.md to this project's stack."
