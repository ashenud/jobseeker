# Milestone 02 - Compliance and Platform Policy Registry

## Goal

Create an enforceable policy layer that decides which operations are allowed for each source. The registry must block unknown or prohibited behavior at runtime.

## Why this matters

A public page is not automatically permission to scrape, and an API endpoint is not automatically permission to submit bids in bulk. Terms, API access, rate limits, storage rules, and account rules can differ. This system must fail closed.

## Policy model

Each platform/action pair receives one mode:

- `disabled` - no use.
- `manual_only` - user pastes or imports content; no automated retrieval.
- `public_feed` - documented RSS/JSON/public API retrieval within published limits.
- `official_api_read` - approved credentials allow discovery/read operations.
- `official_api_write_with_confirmation` - a permitted write API exists, is approved, and every action requires confirmation.
- `internal_test_fixture` - development fixtures only.

Actions are separate: `discover`, `read_detail`, `store`, `notify`, `draft`, `open_link`, `submit`, `message`, and `follow_up`.

## Initial conservative policy

| Platform/source | Discover | Submit | MVP approach |
|---|---|---|---|
| Behance | `manual_only` initially | `manual_only` | User captures job URL/text; app scores/drafts; user applies in Behance UI |
| Upwork | `official_api_read` only after approval, otherwise `manual_only` | `manual_only` | No scraping; import manually or use approved official API |
| Freelancer.com | `official_api_read` when credentials approved | disabled initially; later confirmation-gated | Use official SDK/API and review current API terms |
| Remote OK | `public_feed` after endpoint/terms verification | external manual application | JSON/RSS ingestion |
| Jobicy | `public_feed` after endpoint/guideline verification | external manual application | API/RSS ingestion |
| Email/manual paste | user-authorized | manual | Safe universal fallback |
| Direct outreach | curated/manual list | confirmation-gated only | No bulk prospect scraping or auto-send |

Treat this table as a starting assumption, not permanent legal advice. The implementation must record a review date and reference URL.

## Required deliverables

- `config/platform_policy.yaml`
- `src/job_agent/policy/models.py`
- `src/job_agent/policy/service.py`
- `src/job_agent/policy/exceptions.py`
- CLI command: `job-agent policy check <platform> <action>`
- tests proving blocked actions cannot execute
- `docs/PLATFORM_AUDIT.md`

## Required fields per platform

```yaml
platform_id: behance
display_name: Behance
reviewed_at: 2026-07-18
review_due_at: 2026-10-18
terms_url: "..."
help_or_api_url: "..."
owner_approved: false
actions:
  discover: manual_only
  store: manual_only
  draft: manual_only
  submit: manual_only
limits:
  requests_per_minute: 0
  retention_days: 30
notes: "No confirmed public Jobs API; use user-provided content."
```

## Enforcement rules

1. Every adapter declares a platform and requested action.
2. The policy service authorizes before network or write activity.
3. Missing platform/action entries are denied.
4. Expired policy reviews disable network activity until reviewed.
5. Write actions require both policy permission and a runtime feature flag.
6. Submission additionally requires a short-lived user confirmation token.
7. Audit logs record the policy version used.

## Tests

- unknown platform is denied;
- unknown action is denied;
- expired review is denied;
- `manual_only` prevents network retrieval;
- submission fails without confirmation;
- read permission cannot be reused as write permission;
- configuration validation rejects contradictory settings.

## Codex execution prompt

```text
Implement Milestone 02 only. Build the platform policy registry and fail-closed authorization service. Use the conservative initial table from the document. Add unit tests that prove prohibited and unknown actions cannot reach connector code. Do not implement any live connector yet.
```

## Acceptance criteria

- [ ] Policy is machine-readable and schema-validated.
- [ ] Every future connector must call the policy service.
- [ ] Unknown, expired, and prohibited actions fail closed.
- [ ] Submission requires separate permission, feature flag, and confirmation.
- [ ] Platform terms and review dates are documented.

## Unspoken risk

The biggest account risk is not a coding bug; it is a connector whose assumptions outlive a platform’s terms. Quarterly policy review must become an operating task.
