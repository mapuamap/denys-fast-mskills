# 07 — Test plan (unit + integration)

> E2E lives in `08_e2e_plan.md`. This file covers tests runnable in CI without external systems beyond what fakes can stand in for.

## Test commands
- Run all: `<command>` — e.g. `dotnet test src/TelegramBot.Tests/TelegramBot.Tests.csproj -c Release`
- Run focused subset: `<command with filter>`
- Coverage report: `<command>` (or "not configured")

## Targets
| Module / area | Target coverage | Current | Required new tests |
|----------------|------------------|---------|---------------------|
| <module>       | <…>%             | <…>%    | <count>             |

## Unit tests to add

### <ModuleName>Tests
- `<TestClass>.<MethodName_State_Expected>` — verifies <…>
- `<…>` — verifies <…>
- `<…>` — verifies <…>

### <Other module>Tests
- <…>

## Integration tests to add
- `<TestClass>` — boundary under test: <DB / HTTP / queue>; fake / real: <…>
- <…>

## Regression tests
Every bug touched by this task gets a regression test that **fails on the broken version and passes after the fix**.
| Bug ref | Test name | Failing input |
|---------|-----------|----------------|
| <…>     | <…>       | <…>            |

## Fakes / fixtures
| Boundary | Fake used | Where defined |
|----------|------------|----------------|
| DB       | `InMemory<…>` / `Fake<…>` | <…> |
| HTTP     | `<…>` | <…> |
| Clock    | `FixedClock(…)` | <…> |

## Test data
- Builders / fixtures added: <…>
- Determinism: no `DateTime.Now`, no `Guid.NewGuid()` outside a seam, no `Random()` outside a seam.

## Negative cases (per use case)
| Use case | Invalid input | Expected error |
|----------|---------------|------------------|
| <…>      | <…>           | <DomainException : Foo> |

## Pre-existing failures to preserve
- List any tests currently failing in main that this task does **not** intend to fix. Reference them by full name; `09_verification.md` will list them under "Skipped checks".

## Performance / load test (if applicable)
- Tool: <…>
- Scenario: <…>
- Threshold: <…> ; failing build below threshold: yes/no

## CI integration
- Job name: <…>
- Trigger: <on push / PR>
- Required to pass for merge: yes/no
