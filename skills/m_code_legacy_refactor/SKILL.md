---
name: m_code-legacy-refactor
description: Refactors or modernizes legacy code without changing behavior. Use for old projects, messy modules, monolith slices, characterization tests, seams, dependency injection, ports/adapters, incremental migration, and safe AI-assisted refactoring.
disable-model-invocation: true
---

# m_code-legacy-refactor

Improve legacy code by preserving behavior first, then changing structure in small verified slices.

## Contract

Use `$ARGUMENTS` as the target module, path, feature, or refactor goal.

Default mode:

- If the user asks for analysis: `report-only`.
- If the user asks to refactor/fix: `patch-small`.
- Never combine refactoring with a feature change unless explicitly requested.
- Never do a big-bang rewrite unless the user explicitly accepts that risk.

## Workflow

### 1. Establish baseline

Before editing:

```txt
- check git status
- identify language/framework/package manager
- identify test/typecheck/lint/build commands
- inspect applicable CLAUDE.md, .claude/rules, README, architecture docs, CI
- inspect target public APIs, routes, CLI commands, schemas, migrations, integrations
```

Run safe existing checks when practical:

```txt
test
typecheck
lint
build
```

Record pass/fail/skipped. A failing baseline is not your failure; hiding it is.

### 2. Define the behavior contract

List externally visible behavior that must not change:

```txt
public exports/APIs
request/response shapes
CLI arguments and output
database schema and migrations
auth/permissions
billing/payment behavior
error semantics
logging/observability relied on by users or ops
external service contracts
```

If behavior is unclear, characterize current behavior with tests before restructuring.

### 3. Build a safety net

Prefer tests in this order:

```txt
1. characterization tests around current behavior
2. regression tests for known bugs
3. unit tests for extracted pure logic
4. narrow integration tests for adapters/persistence/serialization
5. minimal E2E tests for critical user paths
```

Test observable behavior. Do not test private implementation just because it is easier.

Use fakes/mocks only at external or nondeterministic boundaries:

```txt
DB
network/API
filesystem
clock/current time
random/ID generation
queue/jobs
email/payment/SMS provider
feature flag service
```

### 4. Map the legacy area

Create a concise map:

```txt
Target area:
Entrypoints:
Core decisions:
Side effects:
Globals/env:
Shared mutable state:
Circular dependencies:
High-risk files:
Current tests:
```

Look for:

```txt
- functions/classes with multiple responsibilities
- business decisions inside controllers/routes/UI handlers
- direct DB/API/filesystem/time/random/env calls in core logic
- constructors that create hard dependencies internally
- global mutable state
- copy-paste business rules
- framework logic mixed with domain rules
- broad utils/helpers/misc files
```

### 5. Introduce seams before moving code

Use the least disruptive seam that works:

```txt
- wrap external API calls behind a small interface/protocol
- pass a clock instead of calling current time directly
- pass ID/random generation instead of generating inside business logic
- introduce a repository/client port for persistence/network access
- extract pure decision logic into a small function/module
- create a composition root for wiring concrete dependencies
```

Do not introduce an interface if it does not create a useful test seam, dependency boundary, or compatibility boundary.

### 6. Refactor one vertical slice

Use this sequence:

```txt
characterize -> extract pure logic -> introduce seam/port -> add adapter -> move orchestration -> delete dead code -> validate
```

A good slice is small enough to review in one diff. Prefer one behavior path over a whole subsystem.

During the slice:

```txt
- keep public API stable
- keep response/output shapes stable
- avoid schema changes
- avoid auth/permission/payment changes
- preserve error semantics unless explicitly changing them
- run the narrowest relevant check after edits
```

### 7. Stop conditions

Stop and report instead of expanding scope when:

```txt
- characterization tests reveal unknown or contradictory behavior
- a refactor requires a behavior change
- baseline failures block validation
- a migration/schema change seems necessary
- auth, permissions, billing, security, or data deletion behavior would change
- the safe slice has grown into a rewrite
```

## Final response format

```txt
Baseline:
- Tests: pass/fail/skipped/not found
- Typecheck: pass/fail/skipped/not found
- Lint: pass/fail/skipped/not found
- Build: pass/fail/skipped/not found

Scope:
- <files/modules>

Behavior contract:
- Must remain unchanged: <items>

Safety net:
- <tests added/updated>

Changes made:
- <path>: <change>

Validation:
- <command>: pass/fail/skipped + reason

Behavior preservation:
- Public API changed: yes/no
- Data model changed: yes/no
- User-visible behavior changed: yes/no

Remaining risks:
- <specific risk>

Next slice:
- <one concrete next refactor>
```
