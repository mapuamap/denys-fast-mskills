---
paths:
  - "**/*test*"
  - "**/*spec*"
  - "tests/**/*"
  - "test/**/*"
---

# m_code test rules

- Test behavior and contracts, not incidental implementation.
- Name tests by scenario and expected outcome.
- Use deterministic inputs: fake clock, fake random, fake external clients, isolated persistence.
- Avoid over-mocking domain code. Mock/fake external boundaries.
- Keep characterization tests for legacy code even if the internal design later changes.
