---
name: m_plan_roll
description: Autonomous "full send" of the m_plan pipeline — plan at large scope and implement, no questions. Forces the full 9-artifact plan, decides every blocker itself (recording assumptions), then chains straight into m_plan_implement and drives to done + deploy + verify without pausing. Use when you explicitly want the whole architect → build → deploy → verify cycle run hands-off on a substantial task. Heavier and far less interactive than /m_plan — reach for it only when you truly want zero questions.
disable-model-invocation: true
---

# m_plan_roll

One-shot, hands-off pipeline: **plan large → implement → deploy → verify**, no questions. A thin wrapper over `m_plan` (Phases 0–1) and `m_plan_implement` (execution) that swaps the interactive parts for autonomous defaults and maximum coverage.

> This trades interactivity for autonomy. It still **cannot fake verification** and still **obeys the hard safety gates** below — those are the only things that can halt or block the run.

## Inputs
- `$ARGUMENTS`: the task. If empty, ask once for the task, then stop asking.

## How it differs from `/m_plan`
`m_plan` asks blockers and right-sizes. `m_plan_roll` does neither — it assumes the most thorough path and decides everything itself.

## Phase 1 — Plan (autonomous, large)

Run `m_plan` Phases 0–1 with these overrides:
- **No `AskUserQuestion`, no blocker batch.** For every blocker in `m_plan`'s `BLOCKERS.md`, pick the safest thorough default yourself. **Record each non-obvious decision** under a `## Assumptions` heading in `01_architecture.md` so the run stays auditable.
- **Force size = large** → write **all 9** artifacts (`01`–`09`), maximum coverage (08 included).
- **Gitignore:** append `.m_plan/` to `.gitignore` by default (no prompt); note it in the run log.
- **No Approve pause.** Do not stop for `Approve? (yes / edit / stop)` — go straight to Phase 2.
- Still obey `m_plan`'s artifact rules: a per-step check in every `05` step, build/test commands live only in `07`, fill every `<…>` placeholder, no secrets / real tokens / prod hostnames.

## Phase 2 — Implement (autonomous)

Immediately invoke `m_plan_implement` and run its Phase B to completion, with these overrides:
- **Auto-answer its prompts:** Resume the plan just written; `Ready? = yes`; no slug-selection question (use the new plan).
- **Deploy runs automatically** once every non-deploy `V-*` is `[x]`/`[~]` (treat it as if the user typed `deploy`) — against the real declared target only, per `06` or the discovered deploy path.
- If a non-deploy `V-*` is itself `[!]` blocked (e.g., the target or a required check is unreachable), the auto-deploy precondition isn't met — mark the dependent `V-DEPLOY-*` / `V-SMOKE-*` `[!]` too, finish everything else, and report PARTIAL. Don't force a deploy and don't hang waiting.
- Walk steps, flip `V-*`, **log deviations immediately**, run the **final `V-*` sweep**, then emit the three-section report.

## Hard safety gates (still apply — never bypassed)

Autonomy means *don't ask for preferences*. It does **not** mean *skip safety*:
- **Never fake verification.** `09_verification.md` still decides done. Local build/unit/dev-server checks never satisfy `V-DEPLOY-*` / `V-SMOKE-*` / `V-E2E-*` (the deploy reality invariant).
- **Can't access a required check** (no real deploy path, or the browser MCP / credentials / URL for a check are missing): do **not** stop the whole run and do **not** fake it — mark that `V-*` `[!]` blocked, log a deviation, and keep going with everything else. Surface it in the final report.
- **Destructive actions on production / shared services** (restarts, migrations, replacing containers, data deletion, reboots): apply the repo/user destructive-action policy. If that policy requires confirmation, this is the **one** place the run pauses — stop at that specific action and report it rather than doing something irreversible unprompted.
- **No secrets / real tokens / prod hostnames** in any artifact or commit.

## Phase 3 — Report

Emit `m_plan_implement`'s three-section report (✅ Done / 🔀 Worked around or changed / ❌ Not done), then append:
- **Assumptions made:** every autonomous decision from Phase 1 (copy from `01`'s `## Assumptions`).
- **Halted on:** any destructive-action gate that paused the run (or "none").
- **Final:** DONE | PARTIAL | BLOCKED. If any `V-*` is `[ ]`/`[!]`, it is not DONE — never close by lying.

## Files in this skill
- `SKILL.md` — this file (orchestrator; execution semantics live in `m_plan` / `m_plan_implement`)
- `evals/evals.json` — test cases
