# 03 — Infrastructure requirements

> Delta only. Reference `infra.md` / `deploy.md` for baseline; do not duplicate. Skip sections marked "none" — don't leave empty placeholders.

## Target environments
| Env | Host / cluster | Purpose for this task |
|-----|----------------|------------------------|
| local | <…> | dev loop |
| staging | <…> | integration + e2e |
| prod  | <…> | release |

## Compute / network / storage delta
> Only list what *changes* because of this task. If nothing, write "none".

## Services / dependencies
| Service | Version | Provisioned? | Owner |
|---------|---------|--------------|-------|
| <…>     | <…>     | yes/no       | <…>   |

## Secrets / config
| Name | Where stored | Provisioned in env? | Rotation policy |
|------|--------------|---------------------|------------------|
| <KEY> | <vault / env / file> | local: y/n, staging: y/n, prod: y/n | <…> |

> Never write real secret values. Placeholders only.

## Migrations
- Migration name: `<timestamp>_<slug>` or "none".
- Direction: forward-only / reversible.
- Lock duration: <…>.
- Downtime window: required / not.
- Backfill: <strategy + volume + duration> or "none".

## Backups & restore
- Pre-deploy backup required: yes/no — `<command>`.

## Monitoring delta
- Existing dashboards covering the changed flow: <links>.
- New alerts: <list with threshold + receiver>, or "none".
- Logging destination: <Logger_MM app + group / other>.

## Access requirements
- Missing access at time of writing: <names + what's needed>, or "none".

## Known infra blockers
- <blocker> — owner <…> — ETA <…>, or "none".
