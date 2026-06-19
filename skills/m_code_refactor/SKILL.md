---
name: m_code_refactor
description: Refactor or restructure code safely in small, behavior-checked slices. Two behavior modes — preserve (legacy modernization, no behavior change) or may-change (architecture improvement) — each runnable as report-only or as a patch. Establishes a baseline and a test safety net before moving code, introduces seams before extraction, and justifies every new abstraction by concrete friction. Use for legacy cleanup, messy modules, monolith slices, dependency-direction fixes, ports/adapters, and AI-testability work.
disable-model-invocation: true
---

# m_code_refactor

Change structure without breaking behavior — in slices small enough to review in one diff.

Two axes decide how you work:

- **Behavior mode**
  - `preserve` (default) — externally visible behavior must not change. For legacy modernization and risk reduction.
  - `may-change` — an architecture or behavior change is the explicit goal. Enter this mode only when the user asks for it.
- **Change strategy**
  - `report-only` — assessment + migration plan, no edits. Default when the user asks for a review or plan.
  - `patch-small` — one safe improvement with checks. Default when the user asks to refactor/fix.
  - `patch-slice` — one vertical slice (extract → seam → adapter → wiring) with tests.

Never fold a feature change into a refactor unless asked, and never do a big-bang rewrite unless the user accepts that risk. A rewrite hides the behavior drift that small slices would surface.

## Contract

Use `$ARGUMENTS` as the target module / path / feature and the goal. If the user named a behavior change, switch to `may-change`; otherwise stay in `preserve`.

Do not apply Clean Architecture, DDD, repositories, services, or interfaces mechanically. Each abstraction has to earn its place (see step 7) — unjustified ceremony makes code *harder* to change, which is the opposite of the point.

The detailed reference catalogs for steps 4–7 and the stop conditions live in `templates/playbook.md` — **read it once before you start a real refactor** (skip for a pure throwaway question). The output skeleton lives in `templates/report_format.md`.

## Workflow

### 1. Establish a baseline

Before editing, pin down what "still works" means. For a large or unfamiliar area, delegate the wide scan to the `m_code-context-scout` agent so file dumps stay out of the main context; keep only its map. Capture the language/tooling, the existing check commands, the governing docs, and the target's public surface (full checklist in `templates/playbook.md`). Run the existing checks when safe via `m_code-test-runner`; record pass/fail/skipped. A failing baseline is not your failure; hiding it is.

### 2. Define the behavior contract

List the externally visible behavior that must hold — strict in `preserve`; in `may-change` it tells you exactly what you are intentionally changing. See the contract checklist in `templates/playbook.md` (APIs, request/response shapes, CLI, schema/migrations, auth, billing, error semantics, external contracts). If behavior is unclear, characterize it with tests *before* restructuring.

### 3. Build the safety net

Add tests in the order that buys the most confidence per line (characterization → regression → unit → narrow integration → minimal E2E — see `templates/playbook.md`). Test observable behavior, not private internals; use fakes/mocks only at external or nondeterministic boundaries (DB, network, filesystem, clock, random/ID, queues, email/payment/SMS, feature flags).

### 4. Map the area and name the friction

From the scout's map and your own targeted reads, identify concrete problems — evidence, not vibes. Match against the friction catalog in `templates/playbook.md` (business logic in handlers, core logic importing infra, hard-built deps, god modules, global state, duplicate rules, leaking infra exceptions, tests needing real externals).

### 5. Pick the smallest useful target shape

Only where it fits — for a small project, fewer files and clearer functions beat five new layers. Use the layer map + dependency rule in `templates/playbook.md` (`entrypoints -> application -> domain`; `application -> ports`; `adapters -> ports`; `domain` imports no infra) as a target, not a mandate.

### 6. Refactor one vertical slice

Sequence: `characterize -> extract pure logic -> introduce seam/port -> add adapter -> move orchestration -> delete dead code -> validate`.

Introduce the seam *before* moving code — a clock parameter, an injected ID generator, a small client interface, a repository port, a composition root for wiring. Use the least disruptive seam that creates a real test or dependency boundary. Keep the slice to one reviewable diff and one behavior path; the in-slice constraints (strict in `preserve`) are in `templates/playbook.md`.

### 7. Justify every abstraction

Recommend an abstraction only if it earns its place against the criteria in `templates/playbook.md` (isolates an external/nondeterministic dep, enables fast tests, enforces dependency direction, protects a public boundary, removes duplicate rules, or localizes a future change). Reject anything that only renames or adds a layer for symmetry — when in doubt, leave it concrete.

### 8. Verify and review

After the slice, run the relevant checks (via `m_code-test-runner`). For structural changes, get an independent read from the `m_code-architecture-reviewer` agent on dependency direction and seams before calling it done — a second pass catches boundary leaks the author stops seeing.

### Stop conditions

Stop and report instead of expanding scope when a stop condition in `templates/playbook.md` is hit (unknown/contradictory behavior surfaced, a `preserve` refactor needs a behavior change, baseline failures block validation, a migration/schema change becomes necessary, auth/billing/security/data-deletion would change, or the slice has grown into a rewrite). That file also lists the changes needing explicit human review even when checks pass.

## Final response format

Emit the report using the skeleton in `templates/report_format.md`.

## Files in this skill
- `SKILL.md` — this file (core workflow)
- `templates/playbook.md` — friction catalog, target shape, abstraction tests, stop conditions (read once before a real refactor)
- `templates/report_format.md` — final response skeleton (read at report time)
- `evals/evals.json` — test cases
