# 01 — Architecture plan

> Fill every section. Empty section = unresolved blocker. Replace `<…>` placeholders.

## Task one-liner
<single sentence describing the change>

## Done definition
<one verifiable sentence — quoted into `09_verification.md`>

## In scope
- <…>

## Out of scope
- <…>

## Components affected

| Component | Path / module | Change kind (new / modify / delete) | Reason |
|-----------|----------------|--------------------------------------|--------|
| <name>    | <path>         | <kind>                              | <why>  |

## Dependency direction (must hold after change)
```
<entrypoints> -> <application> -> <domain>
<application> -> <ports>
<adapters> -> <ports>
```
List any deviation from project rules in `.claude/rules/m_code_core.md` and justify it.

## Seams required for this task
- DB / repository: <port name, owner, fake strategy>
- HTTP / external API: <port name, owner, fake strategy>
- Filesystem / clock / random / env: <only if touched>
- Queue / job / feature flag: <only if touched>

## Data flow diagram (ASCII)
```
<actor> -> <entrypoint> -> <use case> -> <port> -> <adapter> -> <external>
                                       \-> <event / log / metric>
```

## Trade-offs considered
| Option | Pros | Cons | Picked? |
|--------|------|------|---------|
| A: <…> | <…>  | <…>  | yes/no  |
| B: <…> | <…>  | <…>  | yes/no  |

**Decision:** <…>. Reason: <…>.

## Risks
- <risk> — mitigated by <…>
- <risk> — accepted; rollback covers it

## Open questions
- None. All blockers resolved in Phase 0. (If any remain, list here and **stop** before Phase 2.)
