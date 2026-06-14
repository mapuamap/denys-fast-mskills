---
disable-model-invocation: true
---

Full cycle: test plan -> deploy -> testing via Playwright Browser MCP -> fixing -> re-deploy. No confirmations, no pauses — do everything yourself.

## Phase 1: Analyze what changed

1. Read `git log` and `git diff` against main/master — determine EVERYTHING that was changed/added
2. Read `deploy.md` in the project root — understand how to deploy
3. Read `CLAUDE.md` if present — understand the project context
4. Determine the application URL/address for testing (from `deploy.md`, docker-compose, `.env`)

## Phase 2: Test plan

Compose an exhaustive test plan for ALL the new functionality. For each feature/change:

### Smoke tests
- Page opens without errors
- Core elements are present
- Browser console has no errors

### Functional tests
- All new/changed buttons, forms, links work
- CRUD operations if any
- Form validation (valid + invalid data)
- Modals, dropdowns, tabs
- Filters, sorting, pagination if affected

### User scenarios
- Full flow from start to finish for each new feature
- Edge cases: empty data, long strings, special characters, double click
- Back/forward navigation

### Integration
- API requests return correct statuses
- Data is saved and displayed correctly
- Interaction between components

Write the plan to a file (not in plan mode — a regular `test-plan.md` file in the root, overwrite if it exists).

## Phase 3: Deploy

1. Check git status — if there are uncommitted changes, commit immediately
2. Run the deploy EXACTLY per `deploy.md` — no confirmations
3. Wait 10–15 seconds, check logs and the health-check
4. If the deploy failed — fix and retry

## Phase 4: Testing via Playwright Browser MCP

Run ALL tests from the plan via Playwright Browser MCP:
- `browser_navigate` to open pages
- `browser_snapshot` to check state
- `browser_click` for clicks
- `browser_type` to enter text
- `browser_screenshot` for screenshots of problem spots

For EACH test:
1. Perform the action
2. Take a snapshot/screenshot
3. Check the result
4. Record the result: PASS / FAIL + problem description

## Phase 5: Fixing

If there are FAILs:
1. Collect all problems into a list
2. Fix each problem in the code
3. Commit the fixes
4. Re-deploy (following the rules in `deploy.md`)
5. Re-test ONLY the failing tests
6. If FAIL again — repeat (max 3 iterations)

## Phase 6: Final report

Update `test-plan.md` with the results and print:
- Total tests / passed / failed
- List of fixed problems
- Number of deploy iterations
- Remaining problems (if any)
- Status: ALL PASS / NEEDS ATTENTION
