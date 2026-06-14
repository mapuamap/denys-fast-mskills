# 05 — Step-by-step execution plan

> One row = one commit-sized step. **Every step has a per-step check.** A step without a check is a bug in this plan.

## Conventions
- Step IDs: `S01`, `S02`, …
- Branch: `<feat|fix|chore>/<task-slug>`
- Commit policy: see `06_deploy_plan.md` if present, else one commit per step.
- **Build / test commands in per-step checks must be copy-paste identical with the canonical block in `07_test_plan.md`** (if 07 exists, else `CLAUDE.md`). If they diverge — fix the canonical first, then propagate. No paraphrasing.

## Steps

### S01 — <short verb-led title>
- **Files:** `<path1>`, `<path2>`
- **Depends on:** none
- **Change:** <one paragraph>
- **Per-step check:** `<exact command>` — expected: <observable result>
- **If check fails:** <how to diagnose, what to revert>

### S02 — <…>
- **Files:** <…>
- **Depends on:** S01
- **Change:** <…>
- **Per-step check:** <…>
- **If check fails:** <…>

### S<N> — Wire-up + smoke
- **Files:** <entrypoints, DI registration, config>
- **Depends on:** S01..S<N-1>
- **Change:** <…>
- **Per-step check:** Full build + targeted tests; manual smoke of the new flow once.
- **If check fails:** <…>

## Dependency graph
- Linear (S01 → S02 → … → S<N>) — omit graph.
- Otherwise paste ASCII graph here.

## Stop conditions
- Per-step check fails twice with the same root cause → stop, escalate.
- A step grows beyond ~300 LOC → split.
- A step touches files outside `04_implementation_requirements.md` → stop, revise plan.
