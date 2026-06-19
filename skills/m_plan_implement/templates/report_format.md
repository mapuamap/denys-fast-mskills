# Phase C report skeleton — read at report time

Re-read `09_verification.md` from disk first. Emit the report below. Headers stay even if a section is empty (an explicit empty section is information).

```
# Implementation report — <slug>

## ✅ Done as planned
- <V-XXX-YY> — <one-liner with path:line where useful>

## 🔀 Worked around or changed
- <V-XXX-YY or planned item> — plan said: <quote>. Did: <…>. Why: <…>. Impact: <…>.

## ❌ Not done
- <V-XXX-YY> — reason: <blocked / skipped per user / failed: <err>>. Next step: <…>.

## Status
Total: <N>. Done: <…>. Skipped: <…>. Blocked: <…>. Open: <…>.
Final: DONE | PARTIAL | BLOCKED

## Commands run
- <build cmd> → <exit, last 3 lines>
- <test cmd> → <summary>
- e2e: <ids run + outcome>

## Files changed
<grouped diff summary>

## Next smallest step
<one action>
```

If not DONE: name the smallest action that unblocks each open / blocked item.
All three result sections are mandatory; keep empty sections.
