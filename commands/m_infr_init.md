---
disable-model-invocation: true
---

Check whether an `infra.md` file exists in the project root.

If the file ALREADY exists — show its contents and ask: "infra.md already exists. Recreate or edit it?"

If the file does not exist — run a wizard, asking the questions one at a time:

1. **Servers**
   - How many servers / VMs are used?
   - For each: name, IP/domain, OS, role (web, api, worker, db, etc.)

2. **Compute resources**
   - CPU: model, core count
   - GPU: model, count, VRAM
   - RAM: amount

3. **Storage**
   - Disks: type (SSD/HDD/NVMe), capacity, mount points
   - NAS / network storage if any
   - S3 / object storage if any

4. **Network**
   - Internal network between servers
   - VPN, firewall, open ports
   - Domains, DNS, CDN

5. **Services and dependencies**
   - DB: type, version, where it runs
   - Cache (Redis, Memcached)
   - Queues (RabbitMQ, Kafka)
   - Other external services

6. **Access**
   - SSH: keys, users, ports
   - How to reach each server

7. **Specifics**
   - Backups: what, where, how often
   - Monitoring: what is used
   - What can go wrong, known issues

Move to the next question after each answer. When all questions are answered — generate `infra.md` and show a preview to the user. Write the file only after confirmation.

Format of `infra.md`:
```markdown
# Infrastructure: {project name}

## Servers
### {server name}
- **IP:** ...
- **OS:** ...
- **Role:** ...
- **CPU:** ...
- **GPU:** ...
- **RAM:** ...
- **Storage:** ...

## Network
...

## Services
...

## Access
...

## Backups & Monitoring
...

## Known Issues
...
```

After creating `infra.md` — update `CLAUDE.md` in the project root:
- If `CLAUDE.md` does not exist — create it
- Add a section (or append to an existing one):
  ```
  ## Infrastructure
  Infrastructure is described in infra.md. Use /m_infr to view it.
  ```
- Do not overwrite existing `CLAUDE.md` content — only append the Infrastructure section if it is not already there
