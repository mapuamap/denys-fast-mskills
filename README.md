# denys-fast-mskills

A Claude Code plugin bundling Denis's `m_*` workflow toolkit — a disciplined **plan → execute → verify** loop, lightweight deploy/infra context commands, a Playwright full-test loop, and the **m_code** code-quality framework.

Everything here is provider-agnostic and self-contained: no hardcoded paths, no external infrastructure assumptions.

## Install

This repo is its own plugin marketplace.

```
/plugin marketplace add mapuamap/denys-fast-mskills
/plugin install denys-fast-mskills@denys-fast-mskills
```

Then restart Claude Code (or reload plugins). All skills, commands, and agents below become available.

## What's inside

### Skills (auto-available everywhere)

| Skill | Purpose |
|-------|---------|
| **m_plan** | Plan → execute → verify pipeline. Asks blocker questions once, right-sizes the artifact set (tiny/small/medium/large), writes plans under `.m_plan/<slug>/`, then walks them step-by-step. "Done" is decided by `09_verification.md`, not by vibes. |
| **m_plan_implement** | Executes an existing `.m_plan/<slug>/` plan, enforces a real-environment deploy/smoke gate, updates verification, and reports Done / Changed / Not done. |
| **m_code_init_project** | Bootstrap / harden a project for AI-assisted development (CLAUDE.md, rules, seams). |
| **m_code_legacy_refactor** | Safe, behavior-preserving incremental refactoring. |
| **m_code_rules_audit** | Audit code against the project's rules and checks. |
| **m_code_architecture_improvement** | Evidence-based architecture refactoring. |
| **m_code_context_refresh** | Context maintenance and handoff for long sessions. |

### Commands

| Command | Purpose |
|---------|---------|
| `/m_setup` | Install the m_code framework payload (rules + hooks + `scripts/ai-check.sh` + settings) into the current project. |
| `/m_infr_init` · `/m_infr` | Create / view `infra.md` (servers, compute, network, deps). |
| `/m_deploy_init` · `/m_deploy_check` · `/m_deploy` | Create / view / run deploy from `deploy.md`. `/m_deploy` is `logger-mm`-aware for post-deploy log checks. |
| `/m_playwright_fulltest` | Full loop: plan → deploy → Playwright Browser MCP test → fix → re-deploy. |
| `/m_explain` | Plain-language summary of what was just done. |

### Agents

`m_code_architecture_reviewer`, `m_code_context_scout`, `m_code_test_runner` — read-only investigators used by the m_code skills.

## Two planning paths

There are intentionally two deploy/verify styles; pick per task:

- **Lightweight** — `deploy.md` + `infra.md` context files driven by the `/m_deploy*` and `/m_infr*` commands. Fast, good for established projects.
- **Formal** — the `m_plan` artifact pipeline (`01_architecture.md … 09_verification.md`, including `06_deploy_plan.md`). Heavier, good for substantial or risky changes where you want a verification oracle.

## The m_code framework

`/m_setup` lays down project-local enforcement scaffolding:

- `.claude/rules/` — dependency direction, source-file, and test contracts.
- `.claude/hooks/` — inject invariants at session start, protect secret/generated files, mark the repo dirty after edits, and (in strict mode) block stopping until verification ran.
- `scripts/ai-check.sh` — auto-detects npm / Python / Go / Rust and runs the project's checks.
- `.claude/settings.json` (+ `settings.strict.example.json`) — wire the hooks in. Strict mode is opt-in.

The five `m_code_*` skills and three agents are global (they come with the plugin); `/m_setup` only installs the per-repo scaffolding. See `m_code_framework/README-hooks.md`.

## Layout

```
denys-fast-mskills/
├── .claude-plugin/        plugin.json + marketplace.json
├── skills/                7 skills (m_plan, m_plan_implement, 5x m_code)
├── commands/              8 commands
├── agents/                3 m_code agents
└── m_code_framework/      payload /m_setup installs into a target project
    ├── rules/  hooks/  scripts/
    ├── AI_INVARIANTS.md  settings.json  settings.strict.example.json
    ├── README-hooks.md   install.sh
```

## License

Apache-2.0. Copyright 2026 Denis (github.com/mapuamap). See `LICENSE`.
