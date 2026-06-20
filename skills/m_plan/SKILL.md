---
name: m_plan
description: Plan + Execute + Verify pipeline for a user-supplied task. Asks blocker/architectural questions upfront via AskUserQuestion and probes deploy/e2e readiness (real target, access, secrets, browser tooling) before generating artifacts so those blockers surface at plan time, not deploy time, right-sizes the artifact set (4–9 docs depending on task class — tiny/small/medium/large), generates plans under .m_plan/<task-slug>/, then walks them step-by-step updating verification as it goes. /goal mode is opt-in. Use when user invokes /m_plan, says "spec this out and build it", "full plan + execute", asks to plan-and-execute a substantial change, or wants a complete architect → implement → deploy → verify cycle in one skill.
---

# m_plan

Plan → execute → verify. Right-sizes the plan to the task, runs blocker questions in a single batch, executes by default (no `/goal` ceremony unless asked). **Done is decided by `09_verification.md`, not by the agent's judgement.**

## Inputs
- `$ARGUMENTS`: task description. If empty, ask once and wait.

## Phase 0 — Blockers + sizing (one round)

1. **Scan in parallel** (read-only): `git status`, `git log --oneline -10`, `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, `infra.md`, `deploy.md`, top-level tree, package/build manifests, existing `.m_plan/`. For a large or unfamiliar repo, delegate the codebase portion of this scan to the `m_code-context-scout` agent and keep only its map.

2. **Pre-classify task size** by these classes:
   - **tiny** (one file, < 50 LOC, no infra, no migration) → files `01, 04, 05, 09`.
   - **small** (one module, tests required, no infra/deploy delta) → files `01, 04, 05, 07, 09`.
   - **medium** (multi-module, deploy delta, no infra change) → files `01, 02, 04, 05, 06, 07, 09`.
   - **large** (touches infra, migrations, or external contracts) → all 9.
   - **`08` is added on top of ANY size** when the task adds an externally-callable or browser-observable surface (HTTP endpoint, UI page, CLI command, Telegram command) that integration tests can't fully cover — this is the one artifact that crosses size bins (see the Phase 1 table). So a *small* UI change is `01, 04, 05, 07, 08, 09`.
   Skipped artifacts are **not written** — `09_verification.md` only lists sections for files that exist.

3. **Deploy & E2E go/no-go probe.** Run this whenever the task is deployable (size ≥ medium) **or** adds an externally-callable / browser-observable surface (the `08` trigger). The point is to surface the blockers that otherwise only appear at deploy/e2e time — *after the code is already built* — and pull them to *now*. **Do not merely ask; actively check what you can, read-only and non-destructive**, then turn every unmet precondition into an upfront `[!]` blocker:
   - **Real deploy target.** Identify it from `06`/`infra.md`/`deploy.md`/repo ops docs/CI/compose/service files. None unambiguously identifiable for a deployable runtime → blocker. → `V-READY-01`.
   - **Deploy access.** Cheaply verify reachability without changing anything: host resolves (DNS), SSH host configured (`ssh -G <host>` / ssh config entry), CI/deploy command exists, registry/login reachable. Missing → blocker. → `V-READY-02`.
   - **Secrets/credentials.** Are the secrets the deploy + e2e login need present in the env (check **presence, never values**)? Missing → blocker. → `V-READY-03`.
   - **E2E vantage + browser tooling** (only if `08` applies): is a browser MCP actually available here (Playwright/Chrome, or macOS computer-use)? Is the target URL reachable from here (VPN/allowlist — probe with a cheap HEAD/GET if safe)? Missing → blocker. → `V-READY-04`, `V-READY-05`.

   For anything you cannot safely probe from here, ask it as a **mandatory** question in step 4 instead of assuming it will work. Every unmet item becomes a `[!]` `V-READY-*` row in `09` (and is reflected in `03`/`06` when those exist). **A deployable plan with an unresolved deploy/e2e blocker is not "ready" — it ships with the `[!]` visible and the user must clear it or accept it as a known blocker; never plan around it silently or downgrade deploy/e2e to a localhost check.**

4. **Compose blocker questions** from `BLOCKERS.md`. Pick only those whose answer is not obvious from the scan or already settled by the step-3 probe. **Include the size confirmation as one of the questions** (preset the agent's pre-classification as the recommended option). Ask via `AskUserQuestion` in batches of up to 4 (if that tool is unavailable in this harness, ask in chat as one numbered list with lettered options + a recommended default, then stop and wait). Aim for ONE batch; open a second only if an answer surfaces a new blocker. **When step 3 ran, the `Deploy & E2E readiness`, `Environments`, `Secrets & credentials`, and (if `08`) `Browser / UI verification` questions the probe could not answer on its own are MANDATORY, not optional** — never assume deploy or browser access exists.

5. **Pick a kebab-case slug** (max 40 chars). Echo: `Slug: <slug>. Size: <tiny|small|medium|large>. Will write: <list>.` If the probe found any open `V-READY-*` blocker, also echo: `Deploy/E2E blockers: <list>` so it's visible before any artifact is written.

6. **Gitignore.** If `.m_plan/` not in `.gitignore`, **ask explicitly**: `Append .m_plan/ to .gitignore? (yes / no — I'll commit artifacts)`. Default `yes`. Never silent.

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

**Carry the probe's blockers into the artifacts.** Any open `V-READY-*` from Phase 0 step 3 must be written into `09`'s `## Readiness` section as `[!]` (and into `03`/`06` blockers when those files exist) — not dropped. The plan is allowed to proceed with open readiness blockers, but they stay visible and block DONE.

After writing, list paths + one-line summary each. **If any `V-READY-*` is `[!]`, restate those deploy/e2e blockers right above the approval line** so the user sees them before approving. Ask: `Approve? (yes / edit <file> / stop)`. Max 2 edit rounds; on the 3rd, ask `Continue editing or accept and move on?`.

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
