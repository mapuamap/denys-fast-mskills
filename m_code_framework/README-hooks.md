# m_code Claude hooks

`settings.json` is the default safe configuration:

- injects `.claude/AI_INVARIANTS.md` at startup/resume/clear/compact
- blocks direct edits to secret-like and generated paths
- marks the repo dirty after edits
- injects a short post-edit reminder

`settings.strict.example.json` also enables `Stop` guard:

- after edits, Claude cannot stop until verification is run (e.g. via `./scripts/ai-check.sh`, or your project's own deterministic checks: `npm test`, `pytest`, `go test`, `cargo test`)
- failed verification blocks stopping
- skipped verification is allowed only when no runnable checks are detected

To enable strict mode:

```bash
cp .claude/settings.strict.example.json .claude/settings.json
```

Check configured hooks in Claude Code with:

```txt
/hooks
```
