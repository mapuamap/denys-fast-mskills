---
name: m_code_rules_audit
description: Audit code against the rules that actually exist in this repo (CLAUDE.md, .claude/rules, configs, CI) plus the deterministic checks that can run safely — architecture boundaries, tests, typecheck, lint, build, security-sensitive changes. report-only by default. Use for PR/commit readiness and rule-compliance checks; complements /code-review, which is rule-agnostic.
disable-model-invocation: true
---

# m_code_rules_audit

Audit code against the rules that actually exist in the repo and the deterministic checks that can be run safely.

## Contract

Use `$ARGUMENTS` as the target file, directory, branch, diff, PR, or rule focus.

Default mode is `report-only`. Do not edit code unless the user explicitly asks for fixes.

Never claim a check passed unless it ran in this session or the user provided the result.

## Workflow

### 1. Determine scope

If a target is given, audit that target.

If no target is given:

```txt
- audit the current working-tree diff
- if there is no diff, audit the highest-risk project rules and structure
```

Inspect:

```txt
- git status
- git diff / changed files, when available
- target files
- nearby tests
- relevant configs and docs
```

### 2. Load rule sources in order

Read applicable rules from:

```txt
1. User's explicit request
2. CLAUDE.md and .claude/CLAUDE.md
3. .claude/rules/**/*.md
4. nested CLAUDE.md files near target files
5. README, docs/architecture.md, ADRs, contribution guide
6. package/build scripts and test config
7. lint/typecheck/formatter configs
8. CI workflows
9. visible framework/repo conventions
```

If `AGENTS.md` exists but no `CLAUDE.md` imports or mirrors it, report that Claude Code may miss those instructions.

If rules conflict, report the conflict. Do not silently choose the convenient rule.

### 3. Classify risk

Mark these as high-risk areas:

```txt
authentication
authorization/permissions
billing/payments
migrations/schema changes
data deletion or retention
security-sensitive parsing/validation
cryptography/secrets/config
external API contracts
concurrency/race-prone code
production deployment behavior
```

High-risk changes require stronger evidence, tests, and human review.

### 4. Run deterministic checks when safe

Delegate noisy or large-output runs to the `m_code-test-runner` agent and keep only its concise summary plus the exact commands. Prefer repo-defined commands over invented commands:

```txt
format check
lint
typecheck
test
focused test for changed area
integration test only when environment is available
build
security/secret scan if configured
```

Skip destructive, production-touching, or environment-dependent commands unless safe prerequisites are present. Report exact skip reason.

LLM review is not a deterministic check. Treat it as supplementary.

### 5. Audit dimensions

Check only against evidence. For the architecture dimension you can delegate an independent read to the `m_code-architecture-reviewer` agent and fold its findings in:

```txt
Rules compliance:
- Does code follow CLAUDE.md/rules/docs/configs?

Architecture:
- dependency direction
- domain vs application vs adapter boundaries
- direct DB/API/filesystem/env/time/random calls in core logic
- circular dependencies
- broad utils/helpers/misc modules

Testing:
- behavior covered by tests
- regression tests for bug fixes
- test seams at external boundaries
- over-mocking or tests coupled to private implementation

Code quality:
- single responsibility
- naming clarity
- duplication
- type safety
- error handling
- edge cases
- observability where needed

Security:
- validation and escaping
- permission checks
- secret handling
- unsafe command/file/network behavior
- untrusted input and prompt-injection-sensitive surfaces

Delivery:
- docs updated when behavior/API changed
- migration safety
- CI compatibility
```

### 6. Severity rules

Use these severities:

```txt
blocker: should stop merge/commit; correctness/security/data loss/build break/high-risk rule violation
high: likely bug, significant architecture violation, missing test for risky behavior
medium: maintainability/testability issue with clear future cost
low: style, naming, documentation, small cleanup
```

Every finding must include evidence and a concrete fix.

### 7. Fix mode

If the user asks to fix:

```txt
1. fix blockers first
2. make the smallest safe patch
3. do not expand scope
4. rerun relevant checks
5. report remaining findings separately
```

## Final response format

```txt
Audit scope:
- <scope>

Rules inspected:
- <source files/configs>

Checks run:
- <command>: pass/fail/skipped + reason

Findings:
1. [severity] <title>
   Rule/source: <file/config/user instruction>
   Evidence: <path + exact issue>
   Impact: <why it matters>
   Fix: <concrete change>

Compliance summary:
- Ready to commit/merge: yes/no
- Blockers: <count>
- High: <count>
- Medium: <count>
- Low: <count>

Recommended next action:
- <one concrete action>
```

If no issues are found, still state what was inspected and what checks ran. Do not say `fully compliant` unless the relevant rules were inspected and required checks passed.
