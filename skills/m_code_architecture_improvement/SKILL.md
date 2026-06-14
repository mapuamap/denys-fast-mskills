---
name: m_code-architecture-improvement
description: Improves software architecture through evidence-based analysis and small validated changes. Use for architecture review, module boundaries, dependency direction, coupling/cohesion, ports/adapters, test seams, refactor plans, and making code easier for humans and Claude to change safely.
disable-model-invocation: true
---

# m_code-architecture-improvement

Improve architecture only when the change reduces real complexity, increases testability, clarifies dependencies, or isolates change.

## Contract

Use `$ARGUMENTS` as the target module, directory, feature, or architecture goal.

Default mode:

- If the user asks for review or plan: `report-only`.
- If the user asks to implement/refactor/fix: `patch-small`.
- If the target is broad: inspect and choose one high-impact slice; do not redesign the whole repo.

Do not apply Clean Architecture, DDD, microservices, repositories, services, or interfaces mechanically. Architecture is justified only by concrete friction.

## Workflow

### 1. Inspect actual structure

Read relevant files, imports, calls, configs, tests, and docs. Do not infer architecture from folder names alone.

Map:

```txt
Entrypoints:
Application/use-case logic:
Domain/core rules:
External dependencies:
Data flow:
Dependency direction:
Current tests:
High-coupling files:
Unclear responsibilities:
Change hotspots, if visible:
```

For broad codebases, keep exploration bounded. If a subagent is available, use isolated research for wide scanning and keep only the summary in the main context.

### 2. Identify concrete architecture problems

Look for evidence of:

```txt
- business decisions inside controllers/routes/UI handlers/CLI handlers
- domain logic importing framework, DB, HTTP, filesystem, env, clock, random, or adapters
- application services depending on concrete infrastructure
- circular imports
- god services/managers
- modules with multiple unrelated reasons to change
- shared mutable global state
- infrastructure exceptions leaking into domain logic
- broad utils/helpers/misc buckets
- tests requiring real external systems unnecessarily
- constructors/functions creating hard dependencies internally
- duplicate business rules
- abstractions with no test, dependency, or compatibility value
```

### 3. Define the smallest useful target shape

Use this conceptual target only where it fits:

```txt
entrypoints/    thin framework/UI/CLI boundary
application/    use cases, transactions, orchestration, permissions workflow
domain/         pure rules, policies, entities, value objects
ports/          interfaces/protocols for external systems
adapters/       concrete DB/API/filesystem/framework implementations
shared/         narrow primitives only
```

Dependency rule:

```txt
entrypoints -> application -> domain
application -> ports
adapters -> ports
domain -> no infrastructure/framework/global nondeterminism
```

For small projects, prefer fewer folders and clearer functions. A two-file extraction can be better than five new layers.

### 4. Choose a change strategy

Select one:

```txt
report-only: architecture report and migration plan
patch-small: one safe improvement with tests/checks
patch-slice: one vertical slice with tests and wiring
```

Before risky moves, add or adjust tests:

```txt
- characterization tests for current behavior
- unit tests for extracted pure logic
- adapter/integration tests for serialization, DB, API, queues, filesystem
- regression tests for known bugs
```

### 5. Implement safely when requested

Preferred sequence:

```txt
1. Extract pure decision logic.
2. Introduce a seam for the external dependency.
3. Define a narrow port/protocol only if needed.
4. Move concrete infrastructure into an adapter.
5. Wire dependencies at the composition root.
6. Delete dead indirection and duplicate rules.
7. Run relevant checks.
```

Keep public behavior stable unless the user explicitly requested a behavior change.

### 6. Architecture decision rules

Recommend an abstraction only if at least one is true:

```txt
- it isolates an external or nondeterministic dependency
- it enables fast behavior tests
- it enforces dependency direction
- it protects a public compatibility boundary
- it removes duplicate business rules
- it makes future changes local instead of cross-cutting
```

Reject abstractions that only rename existing functions or create ceremony.

### 7. Human review gates

Flag these for human review even if checks pass:

```txt
auth/permissions
billing/payments
migrations/schema/data retention
data deletion
security-sensitive parsing/validation
public API compatibility
deployment/runtime config
cross-service contracts
```

## Final response format

```txt
Architecture assessment:
- Current shape:
- Main friction:
- Target shape:
- Selected strategy: report-only/patch-small/patch-slice

Findings:
1. [severity] <issue>
   Evidence: <path/import/call/test gap>
   Impact: <why it hurts change/testability>
   Recommendation: <specific fix>

Changes made or proposed:
- <path/action>

Validation:
- <command>: pass/fail/skipped + reason

Migration plan:
1. <next small step>
2. <next small step>
3. <next small step>

Risk:
- <remaining risk>
```
