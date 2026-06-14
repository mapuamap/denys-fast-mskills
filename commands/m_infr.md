---
disable-model-invocation: true
---

Read the `infra.md` file in the project root.

If the file does not exist — say: "infra.md not found. Run /m_infr_init to create it."

If the file exists — print a short summary:

**Project:** ...
**Servers:** list (name, IP, role)
**GPU/CPU:** what is available
**RAM/Disks:** capacities
**Network:** specifics (VPN, firewall, ports)
**Dependencies:** DBs, queues, caches, external services

No filler, maximally compact. Do not retell the whole file — only the essentials.
