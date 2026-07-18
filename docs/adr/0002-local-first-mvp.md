# ADR 0002: Local-first Docker MVP

## Status

Proposed (revalidation)

## Context

The owner needs a private application on one Windows PC using WSL 2 and Docker
Desktop. Portfolio evidence, job notes, proposal revisions, outcomes, and secrets
do not justify the tenancy and exposure of a public SaaS before the product
boundary is proven.

## Decision

The MVP is local-first and Docker-only. The host may run Git, Docker/Compose
orchestration, read-only file inspection, Codex control-plane operations, and
thin shell wrappers whose application work is executed through Docker Compose.

All application builds, dependency resolution, Python commands, migrations,
tests, linters, type checks, evaluations, development servers, API processes,
workers, schedulers, release checks, backups, and restores execute inside Docker
containers. PostgreSQL/pgvector and Redis are container services; the dashboard
binds locally by default. Host Python environments are not part of the workflow.

Runtime source, AI, embedding, and notification integrations remain
provider-neutral and disabled or offline in deterministic development modes.
Naming a provider does not select a credential, endpoint, model, or budget.

## Consequences

- Clean-checkout, restart, backup, and restore evidence must reproduce with only
  Docker Engine/Desktop and Docker Compose required on the host.
- Private source material stays in documented private inputs and secret mechanisms.
- PC sleep and offline time are visible local limitations, handled by health and
  stale-source signals rather than hidden hosted behavior.
- A public, remote, or multi-tenant deployment requires a separate ADR covering
  authentication, tenancy, exposure, secret management, and data protection.
