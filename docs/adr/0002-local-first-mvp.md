# ADR 0002: Local-first MVP

## Status

Accepted

## Context

The owner needs a private application that can run on one Windows PC using WSL 2 and Docker Desktop. The system will process sensitive portfolio context, proposal drafts, job notes, outcomes, and possibly client information. A public SaaS deployment would add authentication, tenancy, hosting, privacy, and operational burdens before the product boundary is proven.

## Decision

The MVP is local-first. Runtime services will target the owner’s Windows PC through WSL 2 and Docker Desktop, with a local-only dashboard by default. Persistent services such as PostgreSQL, pgvector, Redis, and workers belong behind Docker Compose in later implementation milestones. Runtime LLM, embedding, notification, and source integrations must use provider-neutral interfaces and support development without paid LLM calls.

Private portfolio data, proposal style, evidence records, and owner notes are private source data. They must not be hardcoded into proposal logic, committed as secrets, or sent to providers except through explicit configured runtime providers and guarded workflows.

## Consequences

- The MVP can be validated without operating a public multi-tenant service.
- Backup, restore, startup, and health checks remain necessary because the local PC may sleep or go offline.
- Future hosted deployment requires a separate ADR covering authentication, tenancy, network exposure, secret management, and data protection.
- Provider-neutral boundaries prevent the app from being coupled to Codex or any single runtime LLM provider.
