---
disable-model-invocation: true
---

Read the `deploy.md` file in the project root.

If the file does not exist — tell the user: "deploy.md not found. Run /m_deploy_init to create it."

If the file exists:
1. Parse the deploy configuration from `deploy.md`
2. If the file describes several modules / services — ask the user which one to deploy (a numbered list)
3. If there is a single module — deploy it right away

During deploy:
- Before deploying, ALWAYS check git status:
  - If there are uncommitted changes — commit them immediately with a meaningful message, no questions asked
  - If there are merge conflicts — resolve automatically if possible; if not, show the conflicts and ask
  - If the tree is clean — continue
- Execute the steps EXACTLY as described in `deploy.md` — no confirmations, no pauses
- After deploy, verify the service works (if `deploy.md` describes a health-check)
- After deploy, ALWAYS review the service logs (docker logs, journalctl, log files — depending on what `deploy.md` specifies)
- Make sure the logs contain no errors, panics, unhandled exceptions, connection refused, etc.
- Wait 10–15 seconds after start and check the logs again to confirm the service is stable
- If a `logger-mm` MCP server is available — use it to read logs after deploy:
  - `apps_list` to find the deployed application
  - `session_tail` to see fresh logs after deploy
  - `recent_errors` to check for new errors
  - This is the priority log source — use it INSTEAD of reading logs manually over SSH when available
- Print a final report:
  - What was deployed, where
  - Health-check: passed / failed
  - Logs: clean / errors found (with quotes)
  - Status: OK / NEEDS ATTENTION
