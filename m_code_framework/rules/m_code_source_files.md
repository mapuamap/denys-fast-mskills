---
paths:
  - "src/**/*"
  - "app/**/*"
  - "lib/**/*"
  - "packages/**/*"
  - "services/**/*"
---

# m_code source file rules

When working inside source directories:

- Keep dependency direction explicit: entrypoints -> application -> domain -> ports; adapters implement ports and are wired at composition root.
- Do not import adapters/infrastructure into domain code.
- Do not read environment variables from domain code.
- Do not call real time/random/network/database from domain code; pass a seam instead.
- Prefer extracting pure functions before moving large structures.
- Preserve public exports unless the task explicitly asks for a breaking change.
