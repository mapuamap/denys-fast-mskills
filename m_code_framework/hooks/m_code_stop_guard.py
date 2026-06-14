#!/usr/bin/env python3
"""Optional strict Stop hook.

Blocks Claude from stopping after edits unless a verification marker exists and
is newer than the last edit marker. This is intentionally used only in
settings.strict.example.json by default.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    event = json.load(sys.stdin)
except Exception:
    event = {}

cwd = Path(event.get('cwd') or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
state = cwd / '.claude' / 'state'
dirty_file = state / 'dirty.json'
verify_file = state / 'last-verification.json'


def git_has_changes() -> bool:
    try:
        proc = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        return bool(proc.stdout.strip())
    except Exception:
        return dirty_file.exists()


def block(reason: str) -> None:
    print(json.dumps({'decision': 'block', 'reason': reason}))
    sys.exit(0)

if not git_has_changes() and not dirty_file.exists():
    sys.exit(0)

if not verify_file.exists():
    block("m_code stop guard: files appear changed but no verification marker exists. Run your project's verification checks (e.g. ./scripts/ai-check.sh, npm test, pytest, go test, cargo test) or focused checks, then summarize results.")

try:
    verify = json.loads(verify_file.read_text(encoding='utf-8'))
except Exception:
    block("m_code stop guard: verification marker is unreadable. Re-run ./scripts/ai-check.sh (or your project's test/lint/typecheck commands).")

verify_time = float(verify.get('timestamp', 0))
status = verify.get('status')

if dirty_file.exists():
    try:
        dirty = json.loads(dirty_file.read_text(encoding='utf-8'))
        dirty_time = float(dirty.get('dirty_since', 0))
    except Exception:
        dirty_time = dirty_file.stat().st_mtime
    if verify_time < dirty_time:
        block('m_code stop guard: code changed after the last verification. Run targeted verification again before stopping.')

if status == 'failed':
    block('m_code stop guard: last verification failed. Fix failures or clearly report the failure before stopping.')

sys.exit(0)
