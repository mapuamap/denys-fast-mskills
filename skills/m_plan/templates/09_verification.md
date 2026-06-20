# 09 — Verification checklist (completion oracle)

> **This file decides "done".** Each item is binary: ✓ or ✗. Empty `[ ]` = not done. **Never delete a row to make it pass.** A row whose concept is genuinely N/A for this task (e.g. no DB → `V-IMPL-04`) may be removed; one that simply doesn't apply yet stays `[~]` with a one-line reason.

Status legend: `[ ]` open · `[x]` done · `[!]` blocked (must list blocker) · `[~]` skipped (must list reason)

## Plan context
- Sized as: `<tiny|small|medium|large>`
- Files written: `<list>`
- Intentionally skipped (by sizing — rules inherited from CLAUDE.md / m_code_core.md / deploy.md): `<list>`

> **Only include sections below whose source file exists.** If `03_infra_requirements.md` was not written, omit the `## Infra` section. Same for `## Code`, `## Deploy`, `## E2E`, `## Test`.

## Readiness — deploy & e2e go/no-go (from the Phase 0 probe; include when the task deploys or has `08`)
> Filled by `/m_plan` Phase 0 step 3: a satisfied precondition is `[x]` with the probe output; an unmet one is `[!]` with the blocker. These are the blockers that otherwise only surface at deploy/e2e time — they must be cleared (or accepted) before DONE.
- [ ] V-READY-01: Real deploy target identified — name host/container/CI/app
- [ ] V-READY-02: Deploy target reachable from here — SSH host configured / CI trigger / registry (paste probe)
- [ ] V-READY-03: Deploy + e2e-login secrets present in target env (presence, not values)
- [ ] V-READY-04: Browser MCP available for e2e — Playwright / Chrome / computer-use (only if `08`)
- [ ] V-READY-05: E2E target URL reachable from here — VPN/allowlist (paste probe; only if `08`)

## Architecture (from `01_architecture.md`)
- [ ] V-ARCH-01: Dependency direction holds in diff — paste check output
- [ ] V-ARCH-02: Seams from 01 present as ports + adapters in code
- [ ] V-ARCH-03: Trade-off decision in 01 reflected in code (cite file/method)

## Implementation (from `04_implementation_requirements.md`)
- [ ] V-IMPL-01: Every hand-written "Files to add" row exists in diff (framework-generated files — EF `*.Designer.cs`, `ModelSnapshot.cs`, codegen, lockfiles — excluded)
- [ ] V-IMPL-02: Every "Files to modify" row appears with the stated change
- [ ] V-IMPL-03: Public signatures in 04 match code verbatim
- [ ] V-IMPL-04: Persistence delta (columns / indexes) matches the migration (skip if no DB change)
- [ ] V-IMPL-05: Performance budget met — measurement + value
- [ ] V-IMPL-06: Any new external dependency (NuGet / npm / pip / cargo / system package) is pinned at exact version with license noted; remove this row if no new deps

## Steps (from `05_step_plan.md`)
- [ ] V-STEP-S01: `<command>` → `<result>`
- [ ] V-STEP-Sxx: …

## Code (optional — if `02_code_requirements.md` exists)
- [ ] V-CODE-01: No new `utils` / `helpers` / `misc` / `manager` modules
- [ ] V-CODE-02: Entrypoints contain no business decisions
- [ ] V-CODE-03: New log lines from 02 are present
- [ ] V-CODE-04: No TODO / FIXME without a tracked follow-up

## Infra (optional — if `03_infra_requirements.md` exists)
- [ ] V-INFRA-01: Required secrets present in target env (confirm presence, not values)
- [ ] V-INFRA-02: Migration applies cleanly on a copy of prod data — paste output
- [ ] V-INFRA-03: Backup taken pre-deploy — artifact path / timestamp
- [ ] V-INFRA-04: Required network access verified — paste output

## Test (optional — if `07_test_plan.md` exists)
- [ ] V-BUILD-01: build command exits 0 — last 5 lines
- [ ] V-TEST-01: test command exits 0 — pass/fail summary
- [ ] V-TEST-02: new tests listed in `07` are present (names) and green
- [ ] V-TEST-03: regression tests fail on pre-fix commit, pass on this commit (manually verified)

## E2E (optional — if `08_e2e_plan.md` exists)
- [ ] V-E2E-SM1: smoke `<id>` passed — artifact: <…>
- [ ] V-E2E-01: scenario E2E-01 passed — artifact: <…>
- [ ] V-E2E-NEG-01: negative NEG-01 passed — artifact: <…>
- [ ] V-E2E-XX: one row per scenario in `08`

## Deploy (optional — if `06_deploy_plan.md` exists)
- [ ] V-DEPLOY-01: PR opened — `<url>`
- [ ] V-DEPLOY-02: PR approved by `<reviewer>` (or "self-merge OK")
- [ ] V-DEPLOY-03: Merged to base
- [ ] V-DEPLOY-04: Deploy executed at `<timestamp>` by `<actor>`
- [ ] V-DEPLOY-05: Post-deploy smoke (from `06` + `08`) green
- [ ] V-DEPLOY-06: Monitoring window observed — no alerts traced to this change

## Skipped checks
List any `[~]`. One-line reason inline. For deploy / security / data-loss skips, also quote the user's `skip ok`.
- <V-XXX-YY>: skipped because <…>

## Blockers
List any `[!]`. The task cannot be DONE while any remains.
- <V-XXX-YY>: blocked on <owner / dependency>, ETA <…>

## Deviations
Log here immediately whenever execution drifts from `01–08`. Phase C of `/m_plan_implement` reads this verbatim into the "🔀 Worked around or changed" report section. Do not reconstruct from memory at end.
- <Sxx / V-XXX-YY> — plan said: <one quote>. Did: <…>. Why: <…>.

## Final assertion
Done iff every checkbox is `[x]` or `[~]` and zero `[!]` remain.

Final status: <DONE | NOT DONE — list failing IDs>
Signed off by: <user>
Timestamp: <…>
