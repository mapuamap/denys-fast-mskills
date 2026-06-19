# Refactor playbook — read once at the start of a real refactor

Reference catalogs for `m_code_refactor` steps 4 (friction), 5 (target shape), 7 (justify abstraction), and the stop conditions. The `SKILL.md` workflow stays the source of order; this file holds the long lists so they don't sit in context until a refactor actually runs.

## Step 1 — Baseline capture

```txt
- language / framework / package manager
- test / typecheck / lint / build commands
- applicable CLAUDE.md, .claude/rules, README, architecture docs, CI
- the target's public surface: exports, routes, CLI, schemas, migrations, integrations
```

Run the existing checks when safe (delegate noisy runs to `m_code-test-runner`, keep only the summary). Record pass/fail/skipped. A failing baseline is not your failure; hiding it is.

## Step 2 — Behavior contract (externally visible behavior that must hold)

```txt
public exports / APIs, request/response shapes
CLI arguments and output
DB schema and migrations
auth / permissions, billing / payments
error semantics, logging/observability others rely on
external service contracts
```

If behavior is unclear, characterize it with tests *before* restructuring — you cannot preserve what you have not pinned down.

## Step 3 — Safety net (add tests in this order, most confidence per line first)

```txt
1. characterization tests around current behavior
2. regression tests for known bugs
3. unit tests for extracted pure logic
4. narrow integration tests for adapters / persistence / serialization
5. minimal E2E for critical user paths
```

Test observable behavior, not private internals just because they are easier to reach. Use fakes/mocks only at external or nondeterministic boundaries: DB, network, filesystem, clock, random/ID, queues, email/payment/SMS, feature flags.

## Step 4 — Friction catalog (name the problem with evidence, not vibes)

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

## Step 5 — Smallest useful target shape

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

## Step 6 — Inside the slice (strict in `preserve`)

```txt
- keep public API and output shapes stable
- avoid schema, auth, permission, and payment changes
- preserve error semantics unless the user is explicitly changing them
- run the narrowest relevant check after each edit (delegate to m_code-test-runner)
```

A good slice fits in one reviewable diff and follows one behavior path, not a whole subsystem.

## Step 7 — Justify every abstraction

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

## Stop conditions

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
