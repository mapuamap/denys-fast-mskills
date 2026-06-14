---
disable-model-invocation: true
---

Install the **m_code framework** (rules, hooks, verification script, AI invariants, settings examples) into the current project.

The framework payload ships inside this plugin under `m_code_framework/`. The `m_code_*` skills and agents are already globally available because the plugin is installed — `m_setup` only lays down the **project-local** enforcement scaffolding (rules + hooks + `scripts/ai-check.sh`) that has to live in each repo.

Steps:

1. Locate the bundled installer. It is at `${CLAUDE_PLUGIN_ROOT}/m_code_framework/install.sh`. The installer is self-locating, so just run it against the current project root:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/m_code_framework/install.sh" "$PWD"
   ```
   If `$CLAUDE_PLUGIN_ROOT` is not set in this environment, find the plugin install directory (commonly under `~/.claude/plugins/`) and run `m_code_framework/install.sh` from there with the current project path as the argument.

2. Read the installer's output and confirm what was laid down. Note specifically whether it preserved an existing `.claude/settings.json` (in that case it wrote `settings.m_code.example.json` — tell the user to merge the hooks block manually).

3. Update `CLAUDE.md` in the project root:
   - If `CLAUDE.md` does not exist — create it.
   - Otherwise append this section only if it is not already present (never overwrite existing content):
     ```
     ## m_code
     Code-quality framework installed. Skills: /m_code_init_project, /m_code_legacy_refactor, /m_code_rules_audit, /m_code_architecture_improvement, /m_code_context_refresh. Verification: ./scripts/ai-check.sh
     ```

4. Say: "Done. Run /m_code_init_project to tailor the rules and CLAUDE.md to this project's stack."
