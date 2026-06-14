#!/usr/bin/env python3
"""Mark that Claude edited/wrote files.

This hook is intentionally silent: it writes local state only and does not add
extra text to Claude's context.
"""
import json
import os
import time
from pathlib import Path
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

cwd = Path(data.get('cwd') or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
state = cwd / '.claude' / 'state'
state.mkdir(parents=True, exist_ok=True)

file_path = None
try:
    file_path = data.get('tool_input', {}).get('file_path')
except Exception:
    pass

payload = {
    'dirty_since': time.time(),
    'hook_event': data.get('hook_event_name'),
    'tool_name': data.get('tool_name'),
    'file_path': file_path,
}
(state / 'dirty.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
