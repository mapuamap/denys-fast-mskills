---
name: m_plan
description: Plan + Execute + Verify pipeline for a user-supplied task. Asks blocker/architectural questions upfront via AskUserQuestion, right-sizes the artifact set (4–9 docs depending on task class — tiny/small/medium/large), generates plans under .m_plan/<task-slug>/, then walks them step-by-step updating verification as it goes. /goal mode is opt-in. Use when user invokes /m_plan, says "spec this out and build it", "full plan + execute", asks to plan-and-execute a substantial change, or wants a complete architect → implement → deploy → verify cycle in one skill.
---

# m_plan

Plan → execute → verify. Right-sizes the plan to the task, runs blocker questions in a single batch, executes by default (no `/goal` ceremony unless asked). **Done is decided by `09_verification.md`, not by the agent's judgement.**

## Inputs
- `$ARGUMENTS`: task description. If empty, ask once and wait.

## Phase 0 — Blockers + sizing (one round)

1. **Scan in parallel** (read-only): `git status`, `git log --oneline -10`, `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, `infra.md`, `deploy.md`, top-level tree, package/build manifests, existing `.m_plan/`.

2. **Pre-classify task size** by these classes:
   - **tiny** (one file, < 50 LOC, no infra, no migration) → files `01, 04, 05, 09`.
   - **small** (one module, tests required, no infra/deploy delta) → files `01, 04, 05, 07, 09`.
   - **medium** (multi-module, deploy delta, no infra change) → files `01, 02, 04, 05, 06, 07, 09`.
   - **large** (touches infra, migrations, or external contracts) → all 9.
   Skipped artifacts are **not written** — `09_verification.md` only lists sections for files that exist.

3. **Compose blocker questions** from `BLOCKERS.md`. Pick only those whose answer is not obvious from the scan. **Include the size confirmation as one of the questions** (preset the agent's pre-classification as the recommended option). Ask via `AskUserQuestion` in batches of up to 4 (if that tool is unavailable in this harness, ask in chat as one numbered list with lettered options + a recommended default, then stop and wait). Aim for ONE batch. Open a second batch only if a first answer surfaces a new blocker.

4. **Pick a kebab-case slug** (max 40 chars). Echo: `Slug: <slug>. Size: <tiny|small|medium|large>. Will write: <list>.`

5. **Gitignore.** If `.m_plan/` not in `.gitignore`, **ask explicitly**: `Append .m_plan/ to .gitignore? (yes / no — I'll commit artifacts)`. Default `yes`. Never silent.

## Phase 1 — Generate artifacts

Write under `.m_plan/<slug>/` using `templates/`. Fill from Phase 0 answers — do not leave `<…>` placeholders unresolved; replace with content or delete the section.

| # | File | Always? |
|---|------|---------|
| 01 | architecture | yes |
| 02 | code requirements | size ≥ medium |
| 03 | infra requirements | size = large |
| 04 | implementation requirements | yes |
| 05 | step plan | yes |
| 06 | deploy plan | size ≥ medium |
| 07 | test plan | size ≥ small |
| 08 | e2e plan | size = large, or task adds externally-callable surface (HTTP endpoint, UI page, CLI command, Telegram command) that integration tests cannot fully cover |
| 09 | verification | yes — sections only for files that exist |

**Single source of truth for commands:** build/test commands live in `07_test_plan.md` (or in CLAUDE.md if there's no 07). Every other file references — never duplicates.

After writing, list paths + one-line summary each. Ask: `Approve? (yes / edit <file> / stop)`. Max 2 edit rounds; on the 3rd, ask `Continue editing or accept and move on?`.

## Phase 2 — Execute (default: direct walk; `/goal` opt-in)

**Execution semantics are identical to `m_plan_implement` Phase B.** Single source of truth — re-read that skill's Phase B section. Summary:
- Walk `05_step_plan.md` in dependency order. Per-step check → flip `V-STEP-Sxx` via `Edit`. Retry once on failure; second failure → `[!]` + stop.
- After steps: build → test → (if `08`) e2e → (if `06` and user types `deploy`) walk `06` like steps walk `05`.
- **Log every deviation from `01–08` immediately** under `## Deviations` in `09` — do not reconstruct at end.
- **Before declaring DONE: final V-* sweep.** For every still-`[ ]` row, attempt a deterministic check from current state; flip what passes.

**Opt-in `/goal` mode** — if the user said "use /goal" or task is large + multi-session, emit the line:
```
/goal Complete every checkbox in .m_plan/<slug>/09_verification.md. For each, run the cited command, paste output into the transcript, flip [ ]→[x]. Stop after <N> turns and explain residual blockers.
```
…and let the user run it.

### Rules during execution
- Never edit `01–08` to shrink scope.
- Never delete a `V-*` row from `09` to make it pass.
- `[~]` skip needs one-line reason inline.
- `[!]` blocker needs blocker description inline + row under "Blockers".
- Commit policy follows `06_deploy_plan.md` if it exists; otherwise one commit per step.
- Deploy steps run only after the user types `deploy` AND all non-deploy `V-*` are `[x]`/`[~]`.

## Phase 3 — Final report

When execution stops (success or partial), re-read `09_verification.md` from disk (including `## Deviations`) and emit:
```
Changed: <files touched, grouped>
Verification: <commands + results>
Deviations: <copy verbatim from 09's ## Deviations — or "none">
Skipped checks: <list with reasons>
Risks: <residual>
Next smallest step: <one action>

Plan: .m_plan/<slug>/
Sized as: <tiny|small|medium|large>
Files written: <comma list>
Intentionally skipped (by sizing): <comma list — covered by CLAUDE.md / m_code_core.md / deploy.md>
```

If any `V-*` is `[ ]` or `[!]`: status is **NOT DONE**. Report the specific blocker. Never close the goal by lying.

## Rules
- No secrets / real tokens / prod hostnames in any artifact.
- Never overwrite an existing `.m_plan/<slug>/` without confirming in-turn.
- Per-step check in `05` is non-optional. A step without one = bug in the plan; fix the plan first.
- Architecture (01) must obey `.claude/rules/m_code_core.md` if present, else the generic rules in `templates/02_code_requirements.md`.

## Files in this skill
- `SKILL.md` — this file
- `BLOCKERS.md` — blocker question bank
- `templates/01..09` — artifact templates (use only those the size calls for)
