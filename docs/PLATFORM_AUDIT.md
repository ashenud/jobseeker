# Platform Audit

Initial policy review date: 2026-07-18. Policy records live in `config/platform_policy.yaml` and are reviewed quarterly. Unknown, expired, disabled, and manual-only network actions fail closed.

| Platform | MVP mode | Notes |
|---|---|---|
| Behance | manual only | User captures job URL/text and submits in Behance UI. |
| Upwork | manual only | No scraping; official API requires separate approval. |
| Remote OK | public feed fixtures by default | Live calls are opt-in and policy-gated. |
| Jobicy | public feed fixtures by default | Live calls are opt-in and policy-gated. |
| Manual/email paste | manual only | User-authorized fallback. |
