# Data Model

Initial durable tables include `raw_jobs` for immutable ingested payloads and `proposal_revisions` for append-only proposal text. Later production hardening can expand this Alembic-managed schema without changing the policy-first boundary.
