# 01 - Docker Local Environment Pattern

- Docker Compose is the default local runtime boundary.
- Keep PostgreSQL, pgvector, Redis, API/web, and worker services in Docker unless a milestone explicitly documents a different local-only command.
- Store database data in named Docker volumes; do not commit runtime database files.
- Services must define health checks where practical and use dependency health conditions instead of sleep loops.
- Expose only local development ports by default.
- Keep environment defaults safe: no real secrets, external writes disabled, and policy modes fail closed.
- Startup docs must include clean checkout commands, migration commands, test commands, backup commands, and teardown commands.
