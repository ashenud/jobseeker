# Milestone 02 - Compliance and Platform Policy Registry

## Recovery gate

Replace informal or stale platform assumptions with schema-validated, versioned,
action-specific policy records. Container tests must prove that unknown, expired,
disabled, and manual-only network/write actions are denied before a mocked HTTP
or connector call. Every allowed live-read record needs a current authoritative
source, owner approval, rate limit, retention, and review date. No marketplace
write mode is enabled by this milestone.

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


## Acceptance criteria

- **M02-AC01:** The canonical and example registries use the same versioned,
  machine-readable schema. Validation rejects unknown fields, duplicate platform
  IDs, incomplete action maps, invalid review dates or limits, and contradictory
  action/mode settings.
- **M02-AC02:** Unknown platforms/actions, disabled modes, stale reviews,
  `manual_only` network attempts, and attempts to reuse read permission for writes
  fail closed before any mocked HTTP or connector call.
- **M02-AC03:** A synthetic write permission still requires owner approval, the
  action-specific runtime feature flag, and a short-lived single-use token bound
  to platform, action, destination, and payload checksum. Missing, mismatched,
  expired, or replayed tokens fail.
- **M02-AC04:** The canonical registry enables neither live network reads nor
  marketplace writes. Candidate read sources record current authoritative
  references, limits, retention, and review dates but remain disabled until the
  owner approval and Milestone 08 live-integration gates pass.
- **M02-AC05:** `job-agent policy check <platform> <action>` returns structured
  JSON and a meaningful exit status, and policy decisions emit secret-free audit
  records containing the decision ID, UTC timestamp, policy version, action,
  result, reason, and review date.

Each acceptance entry in `artifacts/verification/milestone-02.json` must use the
same stable ID and reference real Docker logs, tests, documentation, and review
artifacts.

## Unspoken risk

The biggest account risk is not a coding bug; it is a connector whose assumptions outlive a platform’s terms. Quarterly policy review must become an operating task.
