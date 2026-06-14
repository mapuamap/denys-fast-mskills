# 06 — Deployment plan

> Cross-reference project `deploy.md` if present. Do not duplicate; extend with task-specific deltas.

## Branch & commit policy
- Branch: `<feat|fix|chore>/<task-slug>`
- Base: `<main / develop>`
- Commit style: <Conventional Commits / project style>
- One commit per step (S01..S<N>) — squash at PR merge: <yes/no>
- Sign-off / signing required: <yes/no>

## Pre-merge checklist
- [ ] All per-step checks from `05_step_plan.md` green
- [ ] `dotnet build -c Release` exits 0 (or stack equivalent)
- [ ] `dotnet test -c Release` exits 0 (or stack equivalent)
- [ ] Lint / format clean (or "not configured")
- [ ] Diff self-reviewed for behavior / security / architecture risk
- [ ] CHANGELOG / release notes updated if user-visible

## PR
- Title: `<type>: <one-line summary>`
- Body sections: Summary, Test plan, Rollback, Risk
- Reviewers required: <names / "self-merge OK">
- Linked issue: <…>

## Build artifact
- Image / package name: `<registry>/<name>:<tag>`
- Build location: <local / CI / on-server>
- Reproducibility: <hash / lockfile pinned>

## Pre-deploy
- [ ] Backup of affected DB / files taken — command: `<…>`
- [ ] Maintenance window announced (if needed) — channel: <…>
- [ ] Secrets present in target env (cross-checked against `03_infra_requirements.md`)

## Deploy order
1. <Run migration X>
2. <Push image / pull on server>
3. <Restart service Y>
4. <Run post-deploy task Z>
5. <Smoke check>

## Smoke checks (post-deploy)
| Check | Command / URL | Expected |
|-------|---------------|----------|
| Health | `<…>` | 200 OK |
| Login flow | <…> | <…> |
| Affected feature | <…> | <…> |

## Rollback
- Trigger condition: <error rate / latency / failed smoke>
- Steps:
  1. <…>
  2. <…>
- Time to rollback estimate: <…> minutes
- Data rollback: <reversible migration / restore from backup / not needed>

## Post-deploy monitoring
- Window: <duration> after deploy
- Dashboards to watch: <links>
- Logs to tail: <Logger_MM session / file / kubectl logs>
- Alert thresholds active: <…>

## Communications
- Announce deploy: <where>
- Announce success: <where>
- Announce rollback: <where, who decides>

## Schedule
- Earliest allowed deploy: <date/time + tz>
- Freeze windows blocking: <…>
- Deployer on call: <name>
