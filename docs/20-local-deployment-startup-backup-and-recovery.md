# Milestone 20 - Local Deployment, Startup, Backup, and Recovery

## Goal

Operate the full agent on the owner’s Windows PC with one-command startup, restart resilience, encrypted backups, and a tested restore path.

## Local deployment model

- Windows hosts Docker Desktop.
- WSL 2 stores source code and runs commands.
- Docker Compose runs API, worker, scheduler, PostgreSQL, and Redis.
- Browser accesses `http://127.0.0.1:<port>`.
- PC must remain powered, connected, and Docker running for continuous operation.

## Compose profiles

- `core`: database, Redis, API.
- `workers`: worker and scheduler.
- `notifications`: optional Telegram.
- `dev`: development mounts and tooling.

## Startup

Provide:

```bash
make start
make stop
make status
make update
make backup
make restore BACKUP=...
```

For automatic startup, document Windows Task Scheduler or Docker Desktop startup at user login. Do not promise operation while the PC is off or suspended.

## Backups

Back up:

- PostgreSQL logical dump;
- private configuration/evidence manifests;
- uploaded portfolio source files if selected;
- application version and migration revision.

Do not back up Redis as authoritative state. Encrypt archives and store at least one copy outside the Docker volume. Define rolling retention.

## Restore test

1. Stop services.
2. Create a fresh database volume.
3. Restore backup.
4. Run migrations if required.
5. Rebuild derived caches/embeddings when needed.
6. Verify counts, sample records, login, and health.
7. Record a restore report.

## Updates

- commit clean state;
- backup;
- pull/checkout tagged release;
- rebuild images;
- run migration preview;
- migrate;
- start;
- run smoke checks;
- rollback to previous tag and backup if needed.

## Required deliverables

- production-like Compose profile;
- start/stop/status/update scripts;
- backup, encrypt, restore, and verify scripts;
- Task Scheduler documentation;
- disaster-recovery runbook;
- clean-machine installation test.

## Codex execution prompt

```text
Implement Milestone 20 only. Package the application for local Windows/WSL Docker Compose operation with one-command startup, startup-at-login guidance, encrypted PostgreSQL/private-data backups, restore verification, update/rollback scripts, and a clean-install smoke test. Bind locally and do not expose database or Redis ports.
```

## Acceptance criteria

- [ ] One command starts the full local system.
- [ ] Restart does not duplicate jobs/tasks.
- [ ] Backup contains required authoritative data and no unnecessary cache.
- [ ] Restore is tested into a fresh volume.
- [ ] Update and rollback procedures are reproducible.
- [ ] Documentation clearly states the PC must remain on.
