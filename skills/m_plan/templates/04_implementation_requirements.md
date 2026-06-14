# 04 — Implementation requirements

> Concrete code-level requirements. Reader should be able to start typing after this file.
>
> **Hand-written files only.** Framework-generated artifacts (EF migration `Designer.cs` and `ModelSnapshot.cs`, codegen outputs, `.d.ts` from build, lockfile updates) are NOT listed here — `09_verification.md` excludes them from V-IMPL-01 counting.
>
> **Renames:** record as a single row in `Files to modify` using arrow notation (`old.cs → new.cs`). Do NOT also list in `Files to delete`.

## Files to add
| Path | Purpose | Public API (signatures) |
|------|---------|--------------------------|
| <path> | <…> | <…> |

## Files to modify
| Path | Section / method | Change | Why |
|------|------------------|--------|-----|
| <path> | <…> | <…> | <…> |

## Files to delete
| Path | Why safe to delete |
|------|---------------------|
| <…> | <reference search shows no callers> |

## Contracts / interfaces
```csharp
// or stack equivalent — paste the exact signatures of new interfaces / types
public interface I<…>
{
    <…>;
}
```

## Domain types
| Type | Invariants |
|------|-------------|
| <…>  | <…>         |

## Use cases / commands / handlers
| Name | Input | Output | Error cases |
|------|-------|--------|--------------|
| <…>  | <…>   | <…>    | <…>          |

## Persistence
- Tables / collections touched: <…>
- New columns / fields: <name, type, nullable, default>
- Indexes added / dropped: <…>
- Read query plan acceptable for max expected row count: <yes / measure first>

## External calls
| Provider | Endpoint | Auth | Timeout | Retry policy | Circuit breaker |
|----------|----------|------|---------|---------------|------------------|
| <…>      | <…>      | <…>  | <…>     | <…>           | <…>              |

## Configuration
- New config keys with default + range + env override name.
- Validated at startup with explicit failure (no silent defaults for required values).

## Error contract
| Source | Surfaced as | User message | Logged level |
|--------|-------------|---------------|---------------|
| <…>    | <DomainException : Foo> | <…> | <Error / Warn> |

## Performance budget
- p95 latency target for the new path: <…> ms.
- Memory ceiling: <…>.
- DB queries per request: <…>.

## Backward compatibility
- Migration path for existing consumers: <…>
- Deprecation window: <…>
- Feature flag name (if used): <…>, default <off/on>, owner <…>

## Out-of-scope code changes
- <list explicit non-goals so reviewers don't expect them>
