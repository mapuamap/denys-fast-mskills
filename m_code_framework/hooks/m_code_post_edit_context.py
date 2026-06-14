#!/usr/bin/env python3
"""Inject a short reminder after edits without flooding context."""
import json

msg = """m_code reminder after edit:
- Keep domain/business logic separated from external IO and nondeterminism.
- Add/update behavior tests for changed behavior.
- Run ./scripts/ai-check.sh before final response after code changes.
"""

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": msg
    }
}))
