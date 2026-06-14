---
disable-model-invocation: true
---

Read the `deploy.md` file in the project root.

If the file does not exist — say: "deploy.md not found. Run /m_deploy_init to create it."

If the file exists — print a short summary in this format:

**Project:** ...
**Where:** host, path
**How:** deploy method (docker / git pull / rsync / ...)
**Modules:** list if there are several
**Health-check:** present / absent

No filler, maximally compact. Do not retell the whole file — only the essentials.
