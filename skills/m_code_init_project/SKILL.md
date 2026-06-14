---
name: m_code_init_project
description: Initialize or harden a project for AI-assisted development — CLAUDE.md, .claude/rules, architecture boundaries, seams for nondeterminism, deterministic check commands, first behavior tests, and CI readiness. Use when bootstrapping a new repo or making an existing one safe for repeated Claude-assisted change.
disable-model-invocation: true
---

# m_code_init_project

Initialize a repository so Claude and humans can repeatedly build, test, review, and change it safely.

## Contract

Use `$ARGUMENTS` as the project goal, stack, repo path, and constraints.

Default behavior:

- Empty repo: create the smallest useful baseline.
- Existing repo: harden current conventions; do not overwrite them silently.
- Ambiguous stack: infer from files; if still unclear, state the assumption before editing.
- Do not create or commit secrets, tokens, private keys, production URLs, or real customer data.
- Do not add broad tool permissions or auto-approval rules.

## Workflow

### 1. Inspect before writing

For an existing repo of any size, delegate the wide scan to the `m_code-context-scout` agent and keep only its map — that keeps the raw inspection out of your main context. Read only what is needed:

```txt
- git status
- top-level tree
- package/build files
- README/docs
- test/lint/type/build config
- existing CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, .claude/rules
- CI config if present
```

Report:

```txt
Project kind:
Language/stack:
Package manager:
Existing commands:
Existing tests:
Current architecture shape:
Main gaps:
```

### 2. Create deterministic commands

Prefer ecosystem-native scripts in the existing package/build config.

Define or document:

```txt
install
run/dev
test
test:unit, when useful
test:integration, when useful
typecheck, for typed stacks
lint
format or format:check
build
```

If a command cannot be configured safely, record it as `not configured`; do not invent a fake command.

### 3. Establish minimal boundaries

Use names that fit the stack. Keep the dependency idea even if the folders differ.

```txt
entrypoints/    HTTP routes, CLI handlers, workers, UI event handlers
application/    use cases, orchestration, transactions, permissions workflow
domain/         pure rules, policies, entities, value objects
ports/          protocols/interfaces for external systems
adapters/       DB/API/filesystem/framework implementations
shared/         narrow primitives only; no dumping ground
```

Dependency rule:

```txt
entrypoints -> application -> domain
application -> ports
adapters -> ports
adapters may import infrastructure libraries
domain must not import framework, DB, network, env, filesystem, current time, random, or concrete adapters
```

For small projects, collapse folders and keep boundaries visible through names, imports, and tests. Do not split files only to create layers.

### 4. Add seams for nondeterminism and external systems

Create explicit seams around:

```txt
DB/repository
HTTP/API clients
filesystem
clock/current time
random/ID generation
env/config
queues/jobs
email/payment/SMS providers
feature flags
```

Use dependency injection appropriate to the language: function parameters, constructor parameters, fixtures, providers, interfaces/protocols, or composition-root wiring.

### 5. Add first useful tests

Create tests for observable behavior, not private implementation details.

Minimum baseline:

```txt
- one unit test for pure domain/application behavior
- one adapter/integration test only if an external boundary exists and can be tested safely
- one regression test if the project is being hardened around a known risky path
```

Avoid real production services. Use fakes, local fixtures, test containers, or dedicated test instances.

### 6. Create concise Claude guidance

Create or update root `CLAUDE.md`. Keep it short enough to load every session.

If the repo already has `AGENTS.md`, prefer:

```md
@AGENTS.md

# Claude Code notes
- <Claude-specific command or convention only if needed>
```

Recommended `CLAUDE.md` shape:

```md
# Project guidance

## Project shape
- <one-line project purpose>
- Important code lives in <paths>

## Commands
- Install: <command>
- Test: <command>
- Typecheck: <command or not configured>
- Lint: <command or not configured>
- Build: <command or not configured>

## Architecture rules
- <few specific dependency/boundary rules>

## Testing rules
- <few specific testing rules>

## Done means
- Relevant tests/checks run or explicitly reported as skipped.
- Diff reviewed for behavior, security, and architecture risk.
```

Move large or path-specific rules into `.claude/rules/*.md`. Put repeated task playbooks into skills, not `CLAUDE.md`.

### 7. Add enforcement only when explicit

Guidance files are not enforcement. If a rule must always happen, propose a hook or CI check instead of relying on text instructions.

Do not add hooks, permission changes, or `allowed-tools` unless the user explicitly asks and the rule is deterministic and safe.

### 8. Validate

Run the smallest safe checks available — delegate noisy runs to the `m_code-test-runner` agent and keep only the summary:

```txt
- test or focused test
- typecheck, when configured
- lint or format check, when configured
- build, when configured and safe
```

Never claim a command passed unless it ran in this session or the user provided the result.

## Final response format

```txt
Project baseline:
- Kind:
- Stack:
- Package manager:
- Existing repo: yes/no

Files changed:
- <path>: <purpose>

Architecture baseline:
- Boundaries:
- Seams added:
- Dependency rule:

Commands:
- Install:
- Test:
- Typecheck:
- Lint:
- Build:

Validation:
- <command>: pass/fail/skipped + reason

Remaining gaps:
- <specific gap>

Next step:
- <one concrete next action>
```
