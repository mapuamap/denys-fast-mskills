---
name: m_verify
description: Feature-verification manager. Reads the .m_verify/ ledger of features that were implemented but not yet confirmed working, auto-runs every check AI can do on its own (build/test/lint/HTTP/CLI + Playwright/browser), hands the user a minimal checklist of only what a human must confirm, and spawns background repair agents for anything that fails — without blocking the conversation. Use when user invokes /m_verify, says "what do I need to test", "what's left to verify", "check the pending features", "verify what we built", or after a chunk of implementation work that needs sign-off.
---

# m_verify

A manager for **features that are built but not yet confirmed working**. You are the interactive driver in the main context. You read a ledger, verify everything machine-verifiable yourself, give the human the short list only they can close, and delegate fixes to background agents so the conversation keeps moving.

This is the always-on, hook-fed sibling of `m_plan`'s `09_verification.md`. It is intentionally **separate** — its ledger lives at `.m_verify/`, not inside `.m_plan/`.

## The ledger (canonical format — shared with the Stop hook)

Path: `.m_verify/pending.md` (per project, relative to repo root). Confirmed items are archived to `.m_verify/confirmed.md`.

The Stop hook **appends** candidate items on code-change turns; **you curate** them. Flat list of `## ` sections, identity is the `key:` field, field names are English:

```
# m_verify ledger — features awaiting verification
<!-- schema:1 — appended by the m_verify Stop hook, curated by /m_verify. Flat list of `## ` items keyed by `key:`. Do not hand-edit during a /m_verify run. -->

## Add dark-mode toggle to settings
- key: add-dark-mode-toggle-to-settings
- status: pending          # pending | ai-verifying | needs-human | confirmed | failed | repairing
- who: unknown             # ai | human | unknown
- how: open /settings, toggle theme, page repaints dark and persists on reload
- files: src/settings/Toggle.tsx, src/theme.ts
- added: 2026-06-15
- evidence:
- repair_task:
```

State machine: `pending → ai-verifying → confirmed` (AI proved it) · `pending → needs-human → confirmed` (human confirmed) · `… → failed → repairing → re-verify`. Never delete an item; only change its fields or move it to `confirmed.md`.

## Phase 0 — Load

1. Read `.m_verify/pending.md`. If missing or no open items:
   - Offer to **seed** it from recent work: scan `git diff`/`git log` since the last confirmed item (or the last few commits) and the recent transcript for shipped-but-unverified behavior, and write candidate items. If nothing, say so and stop.
2. Parse items. Summarize: `Open: <N> (pending <a>, needs-human <b>, failed <c>, repairing <d>).`

## Phase 1 — Triage (who verifies what)

For every `pending` item, classify `who` and sharpen `how`:
- **`ai`** — checkable deterministically with no human senses or credentials you lack: unit/integration tests, build, typecheck, lint, a CLI command with expected output, an HTTP/API probe, a DB migration applying, a file/route/signature existing, a Playwright/e2e scenario.
- **`human`** — needs human judgment or access you don't have: visual/UX correctness ("looks right"), subjective behavior, product-decision correctness, anything behind credentials/manual steps the agent genuinely cannot drive, real external-account state.
- When unsure, prefer `ai` and let the check decide; downgrade to `human` only if the check can't be expressed.

Write back `who` and a concrete `how`. Set `ai` items to `ai-verifying`.

## Phase 2 — AI self-verification (delegate the noise)

Run every `ai` item. Keep noisy output **out of the main context**:
- Build / test / lint / typecheck / CLI / HTTP probes → delegate to the **`m_code-test-runner`** agent (returns a compact pass/fail).
- **Playwright / e2e** → run the project's e2e via that runner (`npx playwright test …` etc.). For **live, interactive browser** verification that can't be a headless test, drive it in the main context with whatever browser MCP is available (Playwright/Chrome; never fabricate a browser result — if none is available, mark the item `needs-human` with a note).
- Wide "where is this / how do I exercise it" investigation → **`m_code-context-scout`**.

For each item, update the ledger from disk:
- proved → `status: confirmed`, `evidence:` = the exact command/observation that proved it.
- broke → `status: failed`, `evidence:` = the failure. Then start a repair (Phase 4).
- can't be checked headlessly after all → `status: needs-human` with why.

**Never fake a pass.** A check you couldn't run is `needs-human` or `failed`, never silently `confirmed`.

## Phase 3 — The human checklist

Present to the user, in chat, **only what's left for a human** — the `needs-human` items — as a clean numbered list, each with its exact `how` ("Open X → do Y → you should see Z"). Alongside it, briefly report: how many AI confirmed, and what failed → repair launched (with the repair task id). Do not dump the raw ledger.

## Phase 4 — Interactive loop + background repair

Loop with the user:
- User reports outcomes ("1 ok, 2 broken, 3 ok"). For each:
  - **ok** → `status: confirmed`, `evidence:` = `confirmed by user <date>`. Move to `confirmed.md`.
  - **broken** → `status: failed`, capture what they said under `evidence:`, then **launch a background repair agent**.
- **Repair = delegation, never inline.** Spawn the **`m_verify-repair`** agent with `run_in_background: true`, passing: the item title + `key`, its `files`, the failure description, and `how` (the check it must pass). Set `status: repairing`, `repair_task:` = the agent label/id. **Keep talking to the user** — do not block on the repair.
- When a repair agent returns: re-verify the item (AI check if possible, else flip to `needs-human` with "repaired — please re-check"), update the ledger, and tell the user.
- Continue until every item is `confirmed` (or the user stops).

## Phase 5 — Closeout

Re-read the ledger from disk. Report: `Confirmed: <n> · Needs human: <m> · Repairing: <k> · Still failed: <j>.` Append confirmed items to `.m_verify/confirmed.md` (with date + evidence) and remove them from `pending.md`. If `pending.md` is now empty, leave just its header.

## Rules

- The ledger is the source of truth — read it from disk before and after each phase; don't trust an in-memory copy across delegations.
- Idempotent by `key`. Never duplicate, never delete an item — flip fields or archive.
- Never fabricate verification or browser results.
- **Repair agents edit the working tree but never commit or push** — committing is the user's decision.
- Never write secrets, tokens, or production hostnames into the ledger.
- You do the fixing through agents, not yourself — your job is to keep the verification flow with the human moving while repairs happen in the background.

## Files in this skill
- `SKILL.md` — this file
