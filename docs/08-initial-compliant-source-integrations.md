# Milestone 08 - Initial Compliant Source Integrations

## Goal

Prove the adapter framework with diverse, low-risk sources: one manual source, two documented public feeds/APIs, and an optional official marketplace API only if credentials and policy approval exist.

## Required source set

### 1. Manual capture - mandatory

This is the universal path for Behance, Upwork without approved API access, Fiverr, Contra pages without a feed, and any unknown site. The user pastes a URL and job text or imports a file.

### 2. Jobicy API/RSS - recommended public feed

Implement only after rechecking its current usage guidelines, rate limits, attribution, and data fields. Store the exact policy review reference.

### 3. Remote OK JSON/RSS - recommended public feed

Implement only after rechecking current feed terms and required attribution. Use a descriptive user agent and conservative schedule.

### 4. Freelancer official API - optional in this milestone

Enable read/discovery only after the user obtains approved credentials and reviews API terms. Bid placement remains disabled even if the SDK exposes it.

## Behance-specific approach

Behance has a public job list and normal application UI, but the MVP must not assume a supported Jobs API. Use manual capture:

1. User opens a job.
2. User copies the URL and job content into the local capture form.
3. Agent normalizes, scores, and drafts.
4. Review screen opens the original Behance page and copies the approved proposal.
5. User submits in Behance.

This still automates most of the thinking without risking hidden scraping behavior.

## Polling defaults

- Public feeds: every 30-60 minutes, with jitter.
- Official APIs: follow published limits, default no faster than every 15 minutes.
- Failed source: exponential backoff and circuit breaker.
- Manual imports: immediate.

Schedules are configurable. The initial goal is correctness, not maximum freshness.

## Required deliverables

- concrete adapters and fixture payloads;
- source configuration examples;
- mapping documentation per source;
- attribution handling when required;
- integration tests using recorded sanitized fixtures;
- one dashboard/CLI page showing source health and last run.

## Live-test protocol

Live calls are opt-in and tagged. A live test must:

- check policy review is current;
- use the smallest request;
- print no token;
- store no unexpected PII;
- be excluded from normal CI;
- produce a run receipt.

## Codex execution prompt

```text
Implement Milestone 08 only. Add the manual source plus Jobicy and Remote OK adapters using their currently documented public endpoints after verifying the current official source pages. Add Freelancer read-only support behind a disabled feature flag and skip it if credentials are absent. Do not scrape Behance or Upwork. Add sanitized fixtures and mapping documentation.
```

## Acceptance criteria

- [ ] Manual capture works for any platform.
- [ ] At least two feed/API adapters ingest sanitized real-shaped fixtures.
- [ ] Live calls are optional and policy-gated.
- [ ] Behance and Upwork remain manual unless approved API access is configured.
- [ ] Source health reveals stale, failing, or layout-changed adapters.
- [ ] No write/bid endpoint exists in enabled configuration.
