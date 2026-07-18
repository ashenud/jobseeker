# Architecture

A local modular monolith coordinates policy-gated source adapters, raw storage, normalization, deterministic filtering, structured scoring, evidence retrieval, proposal drafting, human review, manual submission assistance, CRM, workers, and observability. External writes are absent by default and require official permission, feature flag, dry run, idempotency, and confirmation.
