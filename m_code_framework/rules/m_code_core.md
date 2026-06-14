# m_code core rules

These rules apply to all code changes.

## Code shape

- Put business rules where they can be tested without network, database, filesystem, current time, randomness, or framework runtime.
- External systems must be accessed through explicit seams: ports, interfaces, adapters, dependency injection, fakes, or equivalent stack-native boundaries.
- Keep entrypoints thin. Controllers/routes/UI handlers/CLI commands should parse, authorize, call use cases, and return results. They should not contain core business decisions.
- Avoid broad `utils`, `helpers`, `misc`, and `manager` modules unless the name is narrowed by domain and responsibility.
- Do not introduce architecture patterns mechanically. Show the concrete friction the pattern fixes.

## Testing

- Test observable behavior, not private implementation details.
- Add regression tests for bug fixes.
- Use fakes/mocks at nondeterministic or external boundaries only.
- Prefer focused tests during iteration. Run broader checks before final response.

## Reporting

Every final coding response must include:

```txt
Changed:
Verification:
Skipped checks:
Risks:
Next smallest step:
```
