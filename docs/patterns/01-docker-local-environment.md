# 01 - Docker-only environment pattern

- Docker Compose is the only application build, dependency, runtime, migration,
  test, lint, type-check, evaluation, worker, and release boundary.
- Host commands are limited to Git, Docker/Compose orchestration, file inspection,
  Codex control-plane scripts/hooks, and wrappers that exec Docker.
- Pin base image digests for release builds and maintain a real dependency lock.
- Use `api`, `worker`, `scheduler`, `db`, and `redis` services; add test/live-smoke
  profiles when isolation helps.
- Bind Uvicorn to `0.0.0.0` inside its container and publish the host port only on
  `127.0.0.1`.
- Do not publish PostgreSQL or Redis ports by default.
- Health checks must query required dependencies; a static `ready` response fails.
- Use named volumes and prove restart persistence and fresh-volume behavior.
- Keep live source and AI smokes opt-in, bounded, cost-limited, and secret-free.
- `make` and scripts may provide convenience names but must only wrap Compose.

The repo hook blocks common host-native Python toolchain commands. Hooks are
defense in depth; CI and the evidence validator remain authoritative.
