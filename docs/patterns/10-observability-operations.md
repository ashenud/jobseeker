# 10 - Observability and Operations Pattern

- Use structured logs with IDs, event names, state transitions, and outcomes.
- Do not log secrets or full confidential proposal/job texts.
- Track source freshness, ingestion counts, dedupe counts, score distributions, proposal validation failures, policy blocks, and cost usage.
- Provide local health checks for API, database, Redis, workers, and scheduled jobs.
- Backup and restore procedures must be testable from Docker volumes.
- Operational runbooks must match actual commands and failure modes.
