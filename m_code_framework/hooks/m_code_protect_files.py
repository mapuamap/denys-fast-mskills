#!/usr/bin/env python3
"""Deny direct edits to protected or generated paths.

Claude Code PreToolUse hooks should use hookSpecificOutput.permissionDecision
for allow/deny decisions.
"""
import json
import sys
from pathlib import Path

try:
    event = json.load(sys.stdin)
except Exception:
    event = {}

tool_input = event.get("tool_input", {}) if isinstance(event, dict) else {}
file_path = tool_input.get("file_path") or tool_input.get("path") or ""

if not file_path:
    sys.exit(0)

path = file_path.replace("\\", "/")
name = Path(path).name

protected_names = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_ed25519",
}
protected_fragments = [
    "/.git/",
    "/node_modules/",
    "/vendor/",
    "/dist/",
    "/build/",
    "/coverage/",
    "/.next/",
    "/.nuxt/",
    "/.turbo/",
]
protected_suffixes = [
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".sqlite",
    ".db",
]


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)

normalized = "/" + path if not path.startswith("/") else path

if name in protected_names or name.startswith(".env."):
    deny(f"m_code guard: direct edit to environment/secret-like file is blocked: {file_path}")

if any(fragment in normalized for fragment in protected_fragments):
    deny(f"m_code guard: direct edit to protected/generated path is blocked: {file_path}")

if any(path.endswith(suffix) for suffix in protected_suffixes):
    deny(f"m_code guard: direct edit to binary/secret-like file is blocked: {file_path}")

sys.exit(0)
