#!/usr/bin/env bash
set -u

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
STATE="$ROOT/.claude/state"
mkdir -p "$STATE"
LOG="$STATE/last-verify.log"
STATUS="passed"
COMMANDS_RUN=()
COMMANDS_FAILED=()
COMMANDS_SKIPPED=()

: > "$LOG"
echo "m_code verification started at $(date -u +%FT%TZ)" >> "$LOG"
cd "$ROOT" || exit 1

record_skip() {
  local label="$1"
  COMMANDS_SKIPPED+=("$label")
  echo "SKIP: $label"
  echo "SKIP: $label" >> "$LOG"
}

run_cmd() {
  local label="$1"
  shift
  COMMANDS_RUN+=("$label")
  echo "" >> "$LOG"
  echo ">>> $label" >> "$LOG"
  if "$@" >> "$LOG" 2>&1; then
    echo "PASS: $label"
    echo "PASS: $label" >> "$LOG"
  else
    echo "FAIL: $label"
    echo "FAIL: $label" >> "$LOG"
    STATUS="failed"
    COMMANDS_FAILED+=("$label")
  fi
}

has_npm_script() {
  local script="$1"
  python3 - "$script" <<'PY' 2>/dev/null
import json, sys
script = sys.argv[1]
try:
    with open('package.json', encoding='utf-8') as f:
        pkg = json.load(f)
    sys.exit(0 if script in pkg.get('scripts', {}) else 1)
except Exception:
    sys.exit(1)
PY
}

run_npm_script_if_present() {
  local script="$1"
  if has_npm_script "$script"; then
    case "$PM" in
      pnpm) run_cmd "pnpm $script" pnpm run "$script" ;;
      yarn) run_cmd "yarn $script" yarn "$script" ;;
      npm) run_cmd "npm run $script" npm run "$script" ;;
    esac
  else
    record_skip "package script missing: $script"
  fi
}

if [ -f package.json ]; then
  PM="npm"
  [ -f pnpm-lock.yaml ] && PM="pnpm"
  [ -f yarn.lock ] && PM="yarn"

  if [ "$PM" = "pnpm" ] && ! command -v pnpm >/dev/null 2>&1; then
    record_skip "pnpm not installed"
  elif [ "$PM" = "yarn" ] && ! command -v yarn >/dev/null 2>&1; then
    record_skip "yarn not installed"
  elif ! command -v npm >/dev/null 2>&1; then
    record_skip "npm not installed"
  else
    run_npm_script_if_present "lint"
    run_npm_script_if_present "typecheck"
    if has_npm_script "test"; then
      case "$PM" in
        pnpm) run_cmd "pnpm test" pnpm test ;;
        yarn) run_cmd "yarn test" yarn test ;;
        npm) run_cmd "npm test" npm test ;;
      esac
    else
      record_skip "package script missing: test"
    fi
    run_npm_script_if_present "build"
  fi
fi

if [ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ]; then
  if python3 - <<'PY' >/dev/null 2>&1
import pytest
PY
  then
    run_cmd "python3 -m pytest" python3 -m pytest
  else
    record_skip "pytest not installed"
  fi

  if [ -f pyproject.toml ] && python3 - <<'PY' >/dev/null 2>&1
import ruff
PY
  then
    run_cmd "python3 -m ruff check" python3 -m ruff check .
  else
    record_skip "ruff unavailable or no pyproject.toml"
  fi

  if [ -f pyproject.toml ] && python3 - <<'PY' >/dev/null 2>&1
import mypy
PY
  then
    run_cmd "python3 -m mypy" python3 -m mypy .
  else
    record_skip "mypy unavailable or no pyproject.toml"
  fi
fi

if [ -f go.mod ]; then
  if command -v go >/dev/null 2>&1; then
    run_cmd "go test ./..." go test ./...
  else
    record_skip "go not installed"
  fi
fi

if [ -f Cargo.toml ]; then
  if command -v cargo >/dev/null 2>&1; then
    run_cmd "cargo check" cargo check
    run_cmd "cargo test" cargo test
  else
    record_skip "cargo not installed"
  fi
fi

if [ ${#COMMANDS_RUN[@]} -eq 0 ] && [ "$STATUS" = "passed" ]; then
  STATUS="skipped"
fi

export STATE
export M_CODE_STATUS="$STATUS"
export M_CODE_LOG="$LOG"
export M_CODE_COMMANDS_RUN="$(printf '%s\n' "${COMMANDS_RUN[@]}" | python3 -c 'import json,sys; print(json.dumps([l.rstrip("\n") for l in sys.stdin if l.rstrip("\n")]))')"
export M_CODE_COMMANDS_FAILED="$(printf '%s\n' "${COMMANDS_FAILED[@]}" | python3 -c 'import json,sys; print(json.dumps([l.rstrip("\n") for l in sys.stdin if l.rstrip("\n")]))')"
export M_CODE_COMMANDS_SKIPPED="$(printf '%s\n' "${COMMANDS_SKIPPED[@]}" | python3 -c 'import json,sys; print(json.dumps([l.rstrip("\n") for l in sys.stdin if l.rstrip("\n")]))')"

python3 - <<'PY'
import json, os, time
from pathlib import Path
state = Path(os.environ.get('STATE', '.claude/state'))
state.mkdir(parents=True, exist_ok=True)
payload = {
    'timestamp': time.time(),
    'status': os.environ.get('M_CODE_STATUS'),
    'log': os.environ.get('M_CODE_LOG'),
    'commands_run': json.loads(os.environ.get('M_CODE_COMMANDS_RUN', '[]')),
    'commands_failed': json.loads(os.environ.get('M_CODE_COMMANDS_FAILED', '[]')),
    'commands_skipped': json.loads(os.environ.get('M_CODE_COMMANDS_SKIPPED', '[]')),
}
(state / 'last-verification.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
PY

if [ "$STATUS" = "failed" ]; then
  echo "m_code verification failed. See $LOG" >&2
  exit 1
fi

if [ "$STATUS" = "skipped" ]; then
  echo "m_code verification skipped: no runnable checks found. See $LOG"
else
  echo "m_code verification passed. See $LOG"
fi
