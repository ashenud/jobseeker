# Operations

The Milestone 04 local stack uses only Docker Compose:

```bash
make bootstrap
make up
make migrate
make check
make logs
make down
```

`make up` starts the API, Celery worker, Celery beat scheduler, PostgreSQL with
pgvector, and Redis. Check the runtime over the API's local-only published port:

```bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
curl http://127.0.0.1:8000/version
```

Readiness returns `503` and only `up`/`down` component states when PostgreSQL or
Redis cannot be reached. The liveness endpoint remains independent. PostgreSQL
and Redis have no published host ports.

The Windows PC must remain powered on with Docker Desktop running for continuous
operation. `scripts/backup.sh` and `scripts/restore.sh` are later-milestone
scaffolds and are not accepted recovery procedures yet.
