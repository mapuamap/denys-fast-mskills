# 08 — End-to-end test plan (real systems)

> Real DB / real external services / real user-visible interface. Local sandbox or staging. Cover every user-visible flow this task changes. Do not duplicate unit/integration coverage from `07`.

## Environment
- Where: <local docker-compose / staging>
- Bootstrap: `<command(s)>`
- Teardown: `<command(s)>`
- Seed data: <fixture / command>
- External services in scope: <real / sandbox / stubbed — name each>

## Harness
- Browser tool (for UI checks): <Playwright MCP / Chrome MCP / macOS computer-use / none — name what to enable>
- Other tools: <k6 / curl / manual>
- **Access preflight (confirm BEFORE running any browser check):** target URL reachable from here · login required? · test credentials / session available (source; never inline) · network / VPN / allowlist in place.
- If access can't be confirmed (login needed but no creds, URL unreachable, no browser MCP): **stop and ask — never fake a pass or silently skip the browser check.**
- Artifacts (traces / screenshots): <where saved>

## Smoke (post-deploy minimum)
| ID | Check | Command / URL | Expected |
|----|-------|---------------|----------|
| SM1 | <…> | <…> | <…> |

## Scenarios

### E2E-01 — <golden path title>
- Preconditions: <auth, DB state, feature flag, fixtures>
- Steps:
  1. <…>
  2. <…>
- Expected: <observable end state>
- Cleanup: <…>

### E2E-02 — <secondary>
- <…>

## Negative
| ID | Scenario | Expected behavior |
|----|----------|--------------------|
| NEG-01 | <invalid input> | <surfaced error, no partial write> |
| NEG-02 | <external timeout> | <retry / fallback / user-visible error> |

## Edge cases
- Empty state / first-time user
- Boundary values (very large, unicode, RTL)
- Network drop mid-flow
- Browser back / reload mid-flow
- Permission denied for the actor

## Cross-cutting (run once over the suite, not per scenario)
- [ ] No new Error-level logs introduced by these flows.
- [ ] Latency within the budget from `04_implementation_requirements.md`.

## Playwright MCP browser coverage (fill only if the task changes a browser UI)
> Drive each check with concrete Playwright MCP calls (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_screenshot`). For every UI page/feature this task touches, name the selector and the assertion after each action. Skip this whole section for non-UI tasks.

### Per page/feature this task changes
- **Navigation & render:** page opens, key blocks present, `title`/meta correct, no `console.error`.
- **Interactive elements:** every new/changed button, link, tab, dropdown, checkbox, radio, slider; modal open/close + actions inside.
- **Forms:** valid + invalid input for each field; submit, validation messages, double-submit / rapid re-submit guarded.
- **User flows:** full flow end-to-end for each new feature (e.g. login/register, CRUD per entity, filter/sort/paginate, search).
- **Responsive:** mobile 375px, tablet 768px, desktop 1280px.
- **Errors & edge cases:** offline / network drop mid-flow, empty state, very long strings & special chars, browser back/forward, reload mid-flow.
- **Assertions per check:** DOM state after action, API requests return expected statuses, screenshot saved for any flow whose visual state matters (regression baseline).

| ID | Page/feature | Playwright steps (calls + selectors) | Assertion | Artifact |
|----|--------------|--------------------------------------|-----------|----------|
| PW-01 | <…> | navigate <url> → snapshot → click `<sel>` → type `<sel>` "<…>" | <expected DOM / status> | screenshot path |

> PW-* rows map to `V-E2E-*` rows in `09_verification.md` exactly like E2E-* scenarios. Keep IDs stable.

> Scenario IDs (E2E-XX, NEG-XX, SMx, PW-XX) are referenced by `09_verification.md`. Keep IDs stable.
