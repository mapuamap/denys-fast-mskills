# Deploy reality rules — read when this plan deploys anything

Referenced by `m_plan_implement` Phase A (deployment reality gate) and Phase B (deploy walk).
Core invariant: local build / unit / dev-server checks on this workstation are **preflight only** — they never satisfy `V-DEPLOY-*`, `V-SMOKE-*`, or `V-E2E-*` rows unless `06_deploy_plan.md` explicitly declares this workstation as the deployment target. Everything below enforces that one invariant.

## Deployment reality gate (Phase A)

Before editing code, decide whether this plan has an actual runtime surface.
- If the project is a deployed service/app/job: require a real environment target (VM, VPS, NAS, container host, CI/CD target, cloud app, Windows service, browser-served local app, etc.) and at least one remote or externally observable smoke check.
- If the plan claims "no deploy needed", verify that from artifacts and project type. For a deployable runtime, convert that to a blocker/deviation and ask for or infer the real deploy path.
- If the target is production or a shared running service, apply the repo/user destructive-action policy before restarts, migrations, replacing containers, data changes, or reboots.
- If `06` is missing or does not name a real target, inspect repo-local ops docs (`AGENTS.md`, `CLAUDE.md`, `README`, `docs/`, deploy scripts, compose/k8s/systemd files) for an unambiguous deploy path. If still ambiguous, mark deploy as blocked. Do not silently replace deploy with localhost checks.

## Browser verification preflight (Phase A)

If `08_e2e_plan.md` has browser/UI checks (or the task changed a served UI), confirm you can actually run them before you start:
- A **browser MCP is available** — Playwright MCP or Chrome MCP (on macOS without one, computer-use). If none is available, say so and ask the user to enable one; never invent browser results.
- The **target URL is reachable** from here (VPN / allowlist in place).
- If the surface needs **login**, test credentials or a session are available (from the env / user, never hardcoded).
- If unsure whether browser verification is wanted, **ask**. If you can't access it (no MCP, unreachable, login without creds), **stop and ask, or mark the `V-E2E-*` rows `[!]` blocked** — never fake a pass or silently skip.

## Deploy walk (Phase B)

Deploy walks `06` like steps walk `05`, but only against the real target. Run `06`'s "Deploy order" entries in declared order, each followed by its matching smoke check from `06`'s table. Stop on first failure; flip the matching `V-DEPLOY-XX` to `[!]` with the failure line. If `06` says to run commands locally, first confirm those commands actually publish/restart/update the real target; otherwise treat them as preflight, log a deviation, and use the discovered real deploy path or block.

## Real-environment deploy rules

- Deploy verification must observe the real running artifact: `docker ps`/`compose ps` on the host, `systemctl status`, container image/tag/digest, service logs after restart, real HTTP/TCP/API probes, browser check against the served URL, scheduled task status, or equivalent.
- Prefer the estate/project deployment path already documented in repo docs, wiki, scripts, service files, compose files, CI config, or AGENTS/CLAUDE instructions.
- If deploy requires SSH, use the declared host and verify on that host after the command completes. If deploy uses CI/CD, trigger/watch the real pipeline and verify the deployed endpoint.
- For migrations or restarts on production/shared services, read current state first, preserve running state, and ask before destructive actions as required by local operating rules.
- After deploy, run at least one smoke check from the user's perspective or from an external/LAN vantage point, not only inside the build directory.
