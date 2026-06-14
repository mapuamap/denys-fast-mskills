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

## Workflow

### 1. Establish a baseline

Before editing, pin down what "still works" means. For a large or unfamiliar area, delegate the wide scan to the `m_code-context-scout` agent so file dumps stay out of the main context; keep only its map.

Capture:

```txt
- language / framework / package manager
- test / typecheck / lint / build commands
- applicable CLAUDE.md, .claude/rules, README, architecture docs, CI
- the target's public surface: exports, routes, CLI, schemas, migrations, integrations
```

Run the existing checks when safe — delegate noisy runs to the `m_code-test-runner` agent and keep only the summary. Record pass/fail/skipped. A failing baseline is not your failure; hiding it is.

### 2. Define the behavior contract

List the externally visible behavior that must hold (strict in `preserve`; in `may-change` it tells you exactly what you are intentionally changing):

```txt
public exports / APIs, request/response shapes
CLI arguments and output
DB schema and migrations
auth / permissions, billing / payments
error semantics, logging/observability others rely on
external service contracts
```

If behavior is unclear, characterize it with tests *before* restructuring — you cannot preserve what you have not pinned down.

### 3. Build the safety net

Add tests in the order that buys the most confidence per line:

```txt
1. characterization tests around current behavior
2. regression tests for known bugs
3. unit tests for extracted pure logic
4. narrow integration tests for adapters / persistence / serialization
5. minimal E2E for critical user paths
```

Test observable behavior, not private internals just because they are easier to reach. Use fakes/mocks only at external or nondeterministic boundaries: DB, network, filesystem, clock, random/ID, queues, email/payment/SMS, feature flags.

### 4. Map the area and name the friction

From the scout's map and your own targeted reads, identify concrete problems — evidence, not vibes:

```txt
- business decisions inside controllers / routes / UI / CLI handlers
- core logic importing framework, DB, HTTP, filesystem, env, clock, random, or adapters
- constructors that build hard dependencies internally
- god modules; modules with several unrelated reasons to change
- shared mutable global state; circular imports
- duplicate business rules; broad utils/helpers/misc buckets
- infrastructure exceptions leaking into domain logic
- tests that need real external systems unnecessarily
```

### 5. Pick the smallest useful target shape

Only where it fits. For a small project, fewer files and clearer functions beat five new layers.

```txt
entrypoints/  thin framework/UI/CLI boundary
application/  use cases, transactions, orchestration, permissions workflow
domain/       pure rules, policies, entities, value objects
ports/        interfaces/protocols for external systems
adapters/     concrete DB/API/filesystem/framework implementations
shared/       narrow primitives only
```

Dependency rule: `entrypoints -> application -> domain`; `application -> ports`; `adapters -> ports`; `domain` imports no framework / DB / network / env / clock / random / adapters.

### 6. Refactor one vertical slice

Sequence: `characterize -> extract pure logic -> introduce seam/port -> add adapter -> move orchestration -> delete dead code -> validate`.

Introduce the seam *before* moving code — a clock parameter, an injected ID generator, a small client interface, a repository port, a composition root for wiring. Use the least disruptive seam that creates a real test or dependency boundary.

Inside the slice (strict in `preserve`):

```txt
- keep public API and output shapes stable
- avoid schema, auth, permission, and payment changes
- preserve error semantics unless the user is explicitly changing them
- run the narrowest relevant check after each edit (delegate to m_code-test-runner)
```

A good slice fits in one reviewable diff and follows one behavior path, not a whole subsystem.

### 7. Justify every abstraction

Recommend an abstraction only if at least one is true:

```txt
- it isolates an external or nondeterministic dependency
- it enables fast behavior tests
- it enforces dependency direction
- it protects a public compatibility boundary
- it removes duplicate business rules
- it makes a future change local instead of cross-cutting
```

Reject anything that only renames functions or adds a layer for symmetry. When in doubt, leave it concrete — you can extract later when a second caller actually appears.

### 8. Verify and review

After the slice, run the relevant checks (via `m_code-test-runner`). For structural changes, get an independent read from the `m_code-architecture-reviewer` agent on dependency direction and seams before calling it done — a second pass catches boundary leaks the author stops seeing.

### Stop conditions

Stop and report instead of expanding scope when:

```txt
- characterization tests reveal unknown or contradictory behavior
- a preserve refactor turns out to require a behavior change
- baseline failures block validation
- a migration / schema change becomes necessary
- auth, permissions, billing, security, or data-deletion behavior would change
- the safe slice has grown into a rewrite
```

These need explicit human review even if checks pass: auth/permissions, billing/payments, migrations/schema/retention, data deletion, security-sensitive parsing/validation, public API compatibility, deployment/runtime config, cross-service contracts.

## Final response format

```txt
Mode: preserve | may-change · Strategy: report-only | patch-small | patch-slice

Baseline:
- Tests / Typecheck / Lint / Build: pass/fail/skipped/not found

Scope:
- <files/modules>

Behavior contract:
- Must hold: <items>

Safety net:
- <tests added/updated>

Findings:
1. [severity] <issue>
   Evidence: <path/import/call/test gap>
   Impact: <why it hurts change/testability>
   Fix: <specific change>

Changes made or proposed:
- <path>: <change>

Validation:
- <command>: pass/fail/skipped + reason

Behavior preservation (preserve mode):
- Public API changed: yes/no · Data model changed: yes/no · User-visible behavior changed: yes/no

Migration plan / next slices:
1. <next small step>
2. <next small step>

Remaining risk:
- <specific risk>
```

## Files in this skill
- `SKILL.md` — this file
- `evals/evals.json` — test cases
