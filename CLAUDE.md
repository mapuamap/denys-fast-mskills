# CLAUDE.md — denys-fast-mskills (maintainer guide)

You are working on **denys-fast-mskills**, a public Claude Code **plugin** that bundles Denis's `m_*` workflow toolkit. This file is for whoever maintains/extends the plugin — it is dev documentation, not shipped runtime behavior.

- **Repo:** https://github.com/mapuamap/denys-fast-mskills (public, Apache-2.0, owner `mapuamap`)
- **This checkout:** `H:\aps\denys-fast-mskills` — `origin` is set, push to `main` directly.
- **Git identity here:** `mapuamap / doncryptone@gmail.com`.

## What this plugin ships

| Kind | Items |
|------|-------|
| **Skills** (`skills/`) | `m_plan`, `m_plan_implement`, and `m_code_init_project`, `m_code_legacy_refactor`, `m_code_rules_audit`, `m_code_architecture_improvement`, `m_code_context_refresh` |
| **Commands** (`commands/`) | `m_setup`, `m_infr_init`, `m_infr`, `m_deploy_init`, `m_deploy_check`, `m_deploy`, `m_playwright_fulltest`, `m_explain` |
| **Agents** (`agents/`) | `m_code_architecture_reviewer`, `m_code_context_scout`, `m_code_test_runner` |
| **Payload** (`m_code_framework/`) | rules, hooks, `scripts/ai-check.sh`, `AI_INVARIANTS.md`, `settings*.json`, `README-hooks.md`, self-locating `install.sh`. This is NOT auto-loaded — `/m_setup` copies it into a target project's `.claude/`. |
| **Packaging** | `.claude-plugin/plugin.json` (manifest), `.claude-plugin/marketplace.json` (self-marketplace), `README.md`, `LICENSE` |

### Architecture decision (important)
Skills + agents are **plugin-level / global** — they become available in every project once the plugin is installed. `/m_setup` installs only the **project-local enforcement scaffolding** (rules + hooks + `ai-check.sh` + settings), because hooks/rules must live per-repo. Do not move the `m_code_*` skills back into the payload.

### Two planning paths coexist by design
- Lightweight: `infra.md` / `deploy.md` context files driven by `/m_infr*` and `/m_deploy*`.
- Formal: the `m_plan` artifact pipeline (`.m_plan/<slug>/01..09`, where `09_verification.md` is the completion oracle).
Keep both; the README explains when to use which.

## Conventions

- **Language:** everything user-facing is **English**. (Originals were partly Russian; that was translated on first release — keep new content English.)
- **Commands** carry frontmatter `disable-model-invocation: true` (user-triggered only). Keep it on new commands unless you explicitly want model auto-invocation.
- **Skill** = a directory under `skills/<name>/` with `SKILL.md` (YAML frontmatter `name` + `description`, then body). Bundled resources go in subdirs (`templates/`, `evals/`, `BLOCKERS.md`, …).
- **No secrets, no machine-specific paths.** Never commit `H:\...`, `~/bin`, IPs, hostnames, tokens, SSH key names. The one allowed literal is `id_rsa` inside `m_code_framework/hooks/m_code_protect_files.py` — that's a *protection blocklist*, not a secret.
- `m_setup` must stay portable: it shells out to `${CLAUDE_PLUGIN_ROOT}/m_code_framework/install.sh`, which self-locates via `BASH_SOURCE`. Don't hardcode an install source.

## Editing workflow

1. Edit the relevant file under `skills/`, `commands/`, `agents/`, or `m_code_framework/`.
2. If you add/rename a skill or command, update `README.md` and (if structure changed) this file.
3. Bump `version` in `.claude-plugin/plugin.json` for user-visible changes (semver).
4. Validate before committing (see below).
5. Commit + push to `main`. Tag releases if you bump a minor/major version.

## Validate before pushing

```bash
# JSON manifests + evals parse
python -c "import json,glob; [json.load(open(f)) for f in ['.claude-plugin/plugin.json','.claude-plugin/marketplace.json']+glob.glob('skills/**/evals.json',recursive=True)]; print('JSON OK')"

# every skill has frontmatter name+description
for f in skills/*/SKILL.md; do head -5 "$f" | grep -q '^name:' || echo "MISSING name: $f"; done

# leak scan — should return nothing but the id_rsa blocklist line
grep -rniE 'H:\\\\aps|/h/aps|~/bin|192\.168\.|ghp_|gho_|BEGIN .*PRIVATE KEY' . --include='*.md' --include='*.sh' --include='*.py' --include='*.json' | grep -v 'protect_files'

# bash payload sanity
bash -n m_code_framework/install.sh && bash -n m_code_framework/hooks/*.sh && echo "bash OK"
```

## Test the plugin locally

The repo is its own marketplace, so you can install this very checkout:

```
/plugin marketplace add H:\aps\denys-fast-mskills
/plugin install denys-fast-mskills@denys-fast-mskills
```

Then in a scratch project run `/m_setup`, `/m_infr_init`, `/m_plan ...` and confirm they behave. Reload plugins (or restart Claude Code) after edits. For published install others use `/plugin marketplace add mapuamap/denys-fast-mskills`.

## Publish

```bash
git add -A
git commit -m "<what changed>"
git push                      # main -> origin
# optional release tag:
git tag v1.1.0 && git push --tags
```

`gh` is authenticated as `mapuamap`. Repo visibility/topics already set.

## Known follow-ups / ideas

- License badge on GitHub may show "none" briefly after first push — indexer lag; `LICENSE` is valid Apache-2.0.
- `m_plan` Phase 2 references `m_plan_implement` Phase B as the single source of truth for execution — they must ship together (they do). If you split them, fix that cross-reference.
- Consider a CHANGELOG.md once there are multiple releases.
- `ai-check.sh` auto-detects npm/Python/Go/Rust. Extend there if you want more stacks.
