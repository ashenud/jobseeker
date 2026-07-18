# 04 - Database and Migration Pattern

- Use SQLAlchemy 2 models and Alembic migrations for schema changes.
- PostgreSQL is the durable store; pgvector is allowed only through documented migrations and extension setup.
- Add database constraints for invariants; do not rely only on application validation.
- Use idempotency keys and uniqueness constraints for ingestion, jobs, drafts, approvals, submissions, and follow-ups.
- Migrations must be reproducible from a clean Docker database and safe for local data.
- Tests should cover constraints, migrations, deduplication, and state transitions.
