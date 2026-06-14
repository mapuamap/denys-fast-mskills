---
name: m_code-context-refresh
description: Maintains task continuity as context grows. Use before /compact, after /compact, before handoff to a fresh session, after long investigations, or when Claude may be losing project rules. Creates or refreshes HANDOFF.md, reloads core rules, and selects the next m_code workflow.
disable-model-invocation: true
---

# m_code-context-refresh

Keep the task recoverable when the conversation gets long.

## Contract

Use `$ARGUMENTS` as the current task, target directory, or handoff purpose.

Do not make product/code changes unless the user explicitly asks. This workflow is for context maintenance, handoff, and resynchronization.

## Workflow

### 1. Reload durable project context

Read, if present:

```txt
CLAUDE.md
.claude/CLAUDE.md
.claude/AI_INVARIANTS.md
.claude/rules/**/*.md relevant to the current target
docs/ai/HANDOFF.md
README / architecture docs relevant to the current task
```

Summarize only what affects the current task.

### 2. Capture current task state

Inspect:

```txt
git status
git diff --stat
git diff --name-only
recent test or verification outputs if available
```

Do not paste huge diffs. Reference files and summarize.

### 3. Update handoff artifact

Create or update `docs/ai/HANDOFF.md` with:

```md
# AI Handoff

## Current goal

## Non-negotiable rules

## Current plan

## Files changed or investigated

## Behavior/tests already covered

## Verification commands and results

## Open risks / unknowns

## Next smallest action

## Relevant m_code skill to invoke next
```

Keep it compact enough to read at the start of a fresh session.

### 4. Decide next action

Return one of:

```txt
continue-current-session: context is still clean
compact-now: handoff is updated; run /compact and then re-invoke the relevant skill
fresh-session: task should move to a new session using docs/ai/HANDOFF.md
review-first: run /m_code-rules-audit or a review subagent before more edits
```

### 5. After compaction or resume

If invoked after `/compact` or in a fresh session:

1. Re-read `CLAUDE.md`.
2. Re-read `.claude/AI_INVARIANTS.md`.
3. Re-read `docs/ai/HANDOFF.md` if it exists.
4. Re-invoke the most relevant m_code skill.
5. Continue with only the next smallest action.

## Final response

```txt
Context status:
Handoff updated:
Next action:
Relevant skill:
Risks:
```
