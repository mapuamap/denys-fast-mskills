# Final response format — read at report time

```txt
Mode: preserve | may-change · Strategy: report-only | patch-small | patch-slice

Baseline:
- Tests / Typecheck / Lint / Build: pass/fail/skipped/not found

Scope:
- <files/modules>

Behavior contract:
- Must hold: <items>

Safety net:
- <tests added/updated>

Findings:
1. [severity] <issue>
   Evidence: <path/import/call/test gap>
   Impact: <why it hurts change/testability>
   Fix: <specific change>

Changes made or proposed:
- <path>: <change>

Validation:
- <command>: pass/fail/skipped + reason

Behavior preservation (preserve mode):
- Public API changed: yes/no · Data model changed: yes/no · User-visible behavior changed: yes/no

Migration plan / next slices:
1. <next small step>
2. <next small step>

Remaining risk:
- <specific risk>
```
