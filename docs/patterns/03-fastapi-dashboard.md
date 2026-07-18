# 03 - FastAPI Dashboard Pattern

- Use FastAPI for local API routes and server-rendered dashboard pages.
- Use Jinja templates and HTMX/local JavaScript for MVP interactivity; do not introduce React without an ADR.
- Route handlers should delegate business logic to services and return typed schemas or templates.
- Mutating routes must enforce CSRF/session protections appropriate for local deployment before any external write is possible.
- Review screens must show job source, policy mode, score rationale, evidence links, risk flags, and next manual action.
- Proposal approval and submission assistance must be distinct states and UI actions.
