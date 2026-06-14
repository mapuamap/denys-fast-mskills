# Blocker question bank

Draw from this list in Phase 0. Always select the questions that *actually* apply to the task. Skip the ones whose answer is obvious from the scan. Phrase each as a discrete `AskUserQuestion` option set.

## Scope & intent
- What is the single sentence definition of "done" for this task?
- What is explicitly out of scope?
- Is this a behavior change, refactor, infra change, or mix?
- Does this touch a public API / external contract / persisted schema?
- **Size confirmation:** tiny (one file, <50 LOC, no infra/deploy delta) / small (one module + tests) / medium (multi-module + deploy delta) / large (infra / migration / external contract). Used to right-size which artifacts get written.

## Architectural choices
- New module vs extend existing module — preference?
- Sync vs async / batch vs streaming for the new work?
- New table/collection vs reuse existing schema?
- New service boundary vs in-process?
- Feature-flagged rollout or hard cutover?

## Environments
- Where will this run first (local / staging / prod)?
- Which target hosts / containers are in scope?
- Is there a staging environment that mirrors prod for e2e?

## Secrets & credentials
- Are all required secrets already provisioned in the target env? List them.
- Who can rotate / add a missing secret?
- Any new external API keys to obtain before code starts?

## Data & migrations
- Does the task require a DB migration? Forward-only or reversible?
- Is downtime acceptable for the migration window?
- Backfill / data transform needed? Volume estimate?
- Backup taken before migration — automatic or manual?

## Risk & rollback
- What is the blast radius if this ships broken?
- Rollback expectation: redeploy previous tag / DB restore / feature flag off?
- Is a maintenance window required?

## Testing surface
- Unit only, or unit + integration + real e2e?
- Is there a sandbox/test instance of every external dependency?
- Are there existing fixtures / fakes for the affected modules?
- Acceptable to mock the DB, or must integration hit a real DB?

## Browser / UI verification
> Ask when the task adds or changes a browser-observable surface (web page, UI, served app). If unsure whether browser testing is wanted, ask — don't assume.
- Verify the UI in a real browser, or do unit/integration tests cover it? (browser via MCP / no)
- Which browser tool is available here — Playwright MCP, Chrome MCP, or (macOS) computer-use? If none, name what to enable.
- Which URL / environment is verified (local / staging / prod)?
- Does the surface require login/auth? If yes, are test credentials or a session available, and from where? (never hardcode real creds into artifacts)
- Any network / VPN / allowlist needed to reach it?

## Deploy
- CI auto-deploy on merge, or manual trigger?
- Who approves the deploy? You alone or another reviewer?
- Time window restrictions (no Friday deploys, freeze period)?

## Observability
- New logs / metrics required? Where do they go?
- Alert thresholds to set or update?
- Correlation IDs / tracing already in place for this flow?

## External / human dependencies
- Anything blocked on another team or person? Name them.
- Any contract / legal / compliance sign-off required?
- API or library version pinning constraints?

## Time
- Hard deadline?
- Acceptable session length for execution (turn cap for /goal)?
- Should the skill stop at end of plan generation and resume execution later?

## Output preferences
> Gitignore decision is handled by Phase 0 step 5 in `SKILL.md`, not here — do not re-ask.
- One commit per step, or squash at the end?
- Conventional Commits style?
