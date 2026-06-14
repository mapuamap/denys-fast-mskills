---
disable-model-invocation: true
---

Check whether a `deploy.md` file exists in the project root.

If the file ALREADY exists — show its contents and ask: "deploy.md already exists. Recreate or edit it?"

If the file does not exist — run a wizard, asking the questions one at a time:

1. **What are we deploying?**
   - Project / service name
   - If there are several modules — list each

2. **Where are we deploying?**
   - Host (IP/domain), SSH user
   - Path on the server
   - If there are several environments (dev/staging/prod) — describe each

3. **How are we deploying?**
   - Method: docker compose, git pull + restart, rsync, scp, CI/CD, other
   - Build commands
   - Start / restart commands

4. **Database?**
   - Are there migrations, how to run them
   - Backup before deploy?

5. **Environment variables?**
   - Which `.env` files are needed on the server
   - Secrets — where are they stored

6. **Health-check?**
   - URL or command to verify the service works after deploy

7. **Git strategy before deploy?**
   - Auto-commit before deploy needed? (default: yes, ask)
   - Which branch to deploy from (main, develop, current)
   - Push before deploy needed?

8. **Specifics?**
   - Dependencies between services
   - Deploy order
   - What can go wrong

Move to the next question after each answer. When all questions are answered — generate `deploy.md` and show a preview to the user. Write the file only after confirmation.

After creating `deploy.md` — update `CLAUDE.md` in the project root:
- If `CLAUDE.md` does not exist — create it
- Add a section (or append to an existing one):
  ```
  ## Deploy
  Deploy configuration is described in deploy.md. Use /m_deploy to deploy, /m_deploy_check to view the configuration.
  ```
- Do not overwrite existing `CLAUDE.md` content — only append the Deploy section if it is not already there

Format of `deploy.md`:
```markdown
# Deploy: {name}

## Targets
### {environment}
- **Host:** ...
- **User:** ...
- **Path:** ...

## Git
- **Auto-commit before deploy:** yes/no
- **Branch:** main / develop / current
- **Push before deploy:** yes/no

## Build
...

## Deploy steps
1. ...
2. ...

## Rollback
...

## Health-check
...

## Notes
...
```
