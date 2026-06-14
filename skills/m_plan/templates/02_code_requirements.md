# 02 — Code requirements

> Task-specific code rules. Stack-agnostic. Inherit defaults from `.claude/rules/m_code_core.md` and `CLAUDE.md` if present — only restate what's different or load-bearing for this task. Build/test commands live in `07_test_plan.md` if it was written, else in `CLAUDE.md`; never duplicate here.

## Dependency direction (this task)
```
<entrypoints> -> <application> -> <domain>
adapters -> ports
domain MUST NOT import: framework, DB, HTTP, filesystem, env, clock, random, concrete adapters
```

## Seams used by this task
| Seam | Port (interface) | Production adapter | Test adapter |
|------|------------------|--------------------|--------------|
| <…>  | <…>              | <…>                | <…>          |

## Code shape rules
- Business rules live in <module>, testable without external dependencies.
- Entrypoints (<controller / handler / CLI>) parse → authorize → call use case → return. No business decisions.
- No `utils` / `helpers` / `misc` / `manager`. New module names declare domain + responsibility.
- No new architecture pattern without naming the friction it removes.

## Testing rules
- Test framework: <use project default — name it once>.
- Test observable behavior. No private-method tests.
- Regression test required for any bug fix this task addresses.
- Fakes only at seams listed above. No mocking domain logic.

## Error handling
- Validate at boundary: <which>.
- Internal code trusts inputs; no defensive checks where contracts forbid invalid state.
- Wrap external failures into domain errors at the adapter.

## Observability (delta only)
- New log lines: <list with level + key fields>, or "none".
- Correlation ID propagation: <how>, or "n/a".
- Metrics / traces touched: <list>, or "none".

## Code style
- Comments: only where WHY is non-obvious.
- Public API documentation: <required / not>.

## Done means
- Tests in `07` (or `CLAUDE.md` if 07 omitted) run green or explicitly skipped with reason in `09`.
- Build command (canonical block in `07` / `CLAUDE.md`) exits 0.
- Diff reviewed for behavior change, security, architecture risk.
- No new TODO / FIXME without a tracked follow-up.
