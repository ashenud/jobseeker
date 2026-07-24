# ADR 0004: Server-rendered dashboard

## Status

Accepted

## Context

The owner needs a private local review surface for job context, evidence,
proposal revisions, risk flags, approvals, manual packages, and outcomes.
Introducing a separate JavaScript application would add a second build,
dependency graph, API client, authentication surface, and duplicated state
management. The interaction model is primarily forms, tables, filters, and
incremental fragments rather than offline-rich client behavior.

Approval and submission must also remain visibly separate. A browser action that
approves content cannot be allowed to imply a connector call.

## Decision

Use FastAPI with Jinja templates, HTMX, and small repository-local JavaScript for
the MVP. Route handlers validate typed requests, delegate transactions to
application services, and render typed read models or API schemas. They do not
contain state graphs, transaction logic, provider calls, or platform policy
decisions.

OpenAPI remains available for typed local operations. Milestone 05 exposes
architecture/state discovery and transition validation from production
contracts. Mutating review routes introduced later must enforce local
session/CSRF protections. Approval, locking, package preparation, and submission
recording remain separate UI and application commands.

React or another client-side application requires a future ADR with a specific
interaction need and an account of build, security, accessibility, and state
ownership costs.

## Consequences

- The local UI shares the Python deployment and requires no Node toolchain.
- Server-side authorization, validation, escaping, and audit orchestration stay
  close to application services.
- HTMX can update focused fragments without duplicating the domain state graph
  in a browser bundle.
- Browser-driven acceptance tests must prove the human review boundaries, not
  only invoke private service functions.
- Rich offline or highly interactive canvas-style features may be awkward; that
  tradeoff is acceptable for the review-focused MVP.
