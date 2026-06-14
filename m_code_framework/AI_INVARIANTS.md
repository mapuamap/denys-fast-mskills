# AI coding invariants

This file is intentionally short. It is injected after compaction/resume/startup so Claude re-locks onto the core rules.

## Non-negotiable rules

- Domain/business logic must not call database, network, filesystem, env, time, random, or concrete adapters directly.
- External and nondeterministic behavior must go through seams: ports, interfaces, dependency injection, fakes, adapters, providers, or equivalent stack-native mechanisms.
- Legacy refactor starts with behavior characterization or an explicit baseline.
- Make small, reversible changes. Do not combine feature work and refactor work unless the user explicitly asks.
- Add or update tests for changed behavior.
- Never claim verification passed unless it actually ran in this session.
- Final coding response must include changed files, checks run, skipped checks, risks, and next smallest step.

## Context recovery rule

When context feels large or after `/compact`:

1. Read `CLAUDE.md`.
2. Read this file.
3. Read `docs/ai/HANDOFF.md` if it exists.
4. Re-invoke the relevant `/m_code-*` skill.
5. Continue with one smallest useful action.
