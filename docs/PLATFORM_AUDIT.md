# Platform Audit

## Decision boundary

Policy records live in `config/platform_policy.yaml`. Unknown, missing, stale,
`disabled`, and `manual_only` network decisions fail closed before I/O. Manual
capture means the owner supplies content; it does not authorize a connector to
retrieve it. Approval of a draft never authorizes submission, messaging, or a
follow-up.

Milestone 02 enables no live source read and no marketplace write. The candidate
read sources below have current official references and conservative limits, but
remain disabled until explicit owner approval and the bounded Milestone 08 live
integration gate. Fixture behavior is synthetic test configuration, never a mode
in the canonical registry.

## Review record

| Platform | Reviewed | Due | Automated read | External write | Authority and operational notes |
|---|---:|---:|---|---|---|
| Behance | 2026-07-19 | 2026-10-19 | disabled; manual capture only | disabled; owner submits in UI | [Applying guide](https://help.behance.net/hc/en-us/articles/360034476413-Guide-Applying-For-Jobs-On-Behance) and [additional terms](https://wwwimages2.adobe.com/content/dam/cc/en/legal/servicetou/Behance-Additional-Terms-en_US-20221001.pdf); no public Jobs API assumed. Retain owner-supplied records for 30 days. |
| Upwork | 2026-07-19 | 2026-10-19 | disabled; manual capture only | disabled; owner submits in UI | [Developer portal](https://www.upwork.com/developer) and [legal center](https://www.upwork.com/legal); credentials and approved scopes are absent. Retain owner-supplied records for 30 days. |
| Freelancer.com | 2026-07-19 | 2026-10-19 | disabled | disabled | [Developer portal](https://developers.freelancer.com/) and [API terms](https://www.freelancer.com/about/apiterms); no credential or owner approval is recorded. Retain no network payload. |
| Remote OK | 2026-07-19 | 2026-10-19 | disabled candidate JSON/RSS read | disabled; external manual application only | [API endpoint](https://remoteok.com/api) and [current legal terms](https://remoteok.com/legal). Terms require a visible link back wherever API/site data is used. Candidate limit: at most one request per hour; candidate retention: 30 days. |
| Jobicy | 2026-07-19 | 2026-10-19 | disabled candidate API/RSS read | disabled; external manual application only | [Official API/RSS guide](https://jobicy.com/jobs-rss-feed) permits feed integration, prohibits external job-platform redistribution, and says to poll no more than hourly. Candidate limit: one request per hour; candidate retention: 30 days. |
| Manual/email paste | 2026-07-19 | 2027-07-19 | not applicable; owner-provided | manual owner action only | User authorization is record-specific. Retain captured records for 90 days. |
| Direct outreach | 2026-07-19 | 2026-10-19 | disabled | disabled | No bulk list collection or sending. A future proposal needs separate scope, permission, approval, rate limits, confirmation, and audit evidence. |

## Review procedure

Review each record no later than its `review_due_at` date and immediately after a
source terms, API, endpoint, or account-scope change. Record the exact official
reference, action, endpoint, owner decision, rate limit, retention, and
attribution/storage obligations. If any input is uncertain, leave the action
disabled. Enabling a read in Milestone 08 requires updating both the registry and
this audit in the same reviewed change; enabling a write is outside the MVP.
