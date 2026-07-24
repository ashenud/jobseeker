# State machines

The enums and allowed edges below are canonical in
`job_agent.core.states`. Every mutation is a `TransitionCommand` executed by the
transition application service. Self-transitions, unlisted edges, cross-machine
edges, and all outgoing edges from terminal states are forbidden.

## Job

States:

```text
DISCOVERED NORMALIZED DUPLICATE RULE_REJECTED READY_TO_SCORE
SCORED SCORE_FAILED LOW_FIT READY_TO_DRAFT DRAFTED DRAFT_FAILED
IN_REVIEW SKIPPED NEEDS_EDIT APPROVED READY_TO_SUBMIT
SUBMITTED_MANUAL SUBMITTED_API SUBMISSION_CANCELLED
REPLIED INTERVIEW WON LOST WITHDRAWN
```

Every allowed edge:

```text
DISCOVERED -> NORMALIZED
NORMALIZED -> DUPLICATE
NORMALIZED -> RULE_REJECTED
NORMALIZED -> READY_TO_SCORE
READY_TO_SCORE -> SCORED
READY_TO_SCORE -> SCORE_FAILED
SCORED -> LOW_FIT
SCORED -> READY_TO_DRAFT
READY_TO_DRAFT -> DRAFTED
READY_TO_DRAFT -> DRAFT_FAILED
DRAFTED -> IN_REVIEW
IN_REVIEW -> SKIPPED
IN_REVIEW -> NEEDS_EDIT
IN_REVIEW -> APPROVED
APPROVED -> READY_TO_SUBMIT
READY_TO_SUBMIT -> SUBMITTED_MANUAL
READY_TO_SUBMIT -> SUBMITTED_API
READY_TO_SUBMIT -> SUBMISSION_CANCELLED
SUBMITTED_MANUAL -> REPLIED
SUBMITTED_MANUAL -> INTERVIEW
SUBMITTED_MANUAL -> WON
SUBMITTED_MANUAL -> LOST
SUBMITTED_MANUAL -> WITHDRAWN
SUBMITTED_API -> REPLIED
SUBMITTED_API -> INTERVIEW
SUBMITTED_API -> WON
SUBMITTED_API -> LOST
SUBMITTED_API -> WITHDRAWN
REPLIED -> INTERVIEW
REPLIED -> WON
REPLIED -> LOST
REPLIED -> WITHDRAWN
INTERVIEW -> WON
INTERVIEW -> LOST
INTERVIEW -> WITHDRAWN
```

Terminal states are `DUPLICATE`, `RULE_REJECTED`, `SCORE_FAILED`, `LOW_FIT`,
`DRAFT_FAILED`, `SKIPPED`, `NEEDS_EDIT`, `SUBMISSION_CANCELLED`, `WON`, `LOST`,
and `WITHDRAWN`. A retry or revised source creates the appropriate new run or
revision; it does not silently move a terminal record backward.

## Proposal revision

States:

```text
GENERATING GENERATED VALIDATING VALID INVALID IN_REVIEW
EDITED APPROVED REJECTED LOCKED_FOR_SUBMISSION
```

Every allowed edge:

```text
GENERATING -> GENERATED
GENERATED -> VALIDATING
VALIDATING -> VALID
VALIDATING -> INVALID
VALID -> IN_REVIEW
IN_REVIEW -> EDITED
IN_REVIEW -> APPROVED
IN_REVIEW -> REJECTED
APPROVED -> LOCKED_FOR_SUBMISSION
```

Terminal states are `INVALID`, `EDITED`, `REJECTED`, and
`LOCKED_FOR_SUBMISSION`. An edit produces an immutable `EDITED` revision and a
new revision starts its own lifecycle. In particular,
`LOCKED_FOR_SUBMISSION -> EDITED` is forbidden. Approval only confirms the
reviewed content and permits the separate lock/package workflow; it never
submits.

## Application

The application aggregate is authoritative for package preparation, submission
cancellation, the method by which submission was recorded, and outcomes.

States:

```text
READY_TO_PREPARE PACKAGE_PREPARED SUBMISSION_CANCELLED
SUBMITTED_MANUAL SUBMITTED_API REPLIED INTERVIEW WON LOST WITHDRAWN
```

Every allowed edge:

```text
READY_TO_PREPARE -> PACKAGE_PREPARED
PACKAGE_PREPARED -> SUBMISSION_CANCELLED
PACKAGE_PREPARED -> SUBMITTED_MANUAL
PACKAGE_PREPARED -> SUBMITTED_API
SUBMITTED_MANUAL -> REPLIED
SUBMITTED_MANUAL -> INTERVIEW
SUBMITTED_MANUAL -> WON
SUBMITTED_MANUAL -> LOST
SUBMITTED_MANUAL -> WITHDRAWN
SUBMITTED_API -> REPLIED
SUBMITTED_API -> INTERVIEW
SUBMITTED_API -> WON
SUBMITTED_API -> LOST
SUBMITTED_API -> WITHDRAWN
REPLIED -> INTERVIEW
REPLIED -> WON
REPLIED -> LOST
REPLIED -> WITHDRAWN
INTERVIEW -> WON
INTERVIEW -> LOST
INTERVIEW -> WITHDRAWN
```

Terminal states are `SUBMISSION_CANCELLED`, `WON`, `LOST`, and `WITHDRAWN`.
`PACKAGE_PREPARED` means a local immutable package exists; it does not mean a
remote action occurred. `SUBMITTED_MANUAL` records an owner-supplied reference
after the owner acted outside the application. `SUBMITTED_API` is reserved for a
future separately authorized connector and cannot be reached by approval or a
retryable transition worker alone.

## Cross-aggregate ownership

- Proposal owns content revision, factuality validation, human review, approval,
  rejection, and locking.
- Application owns the prepared package, cancellation, submission method and
  reference, and outcomes.
- Job owns discovery-to-review routing and exposes summary submission/outcome
  states for queues.

The application state is authoritative wherever its names overlap the job
summary. A projection to the job summary must follow the corresponding job edge
inside an explicit application service. Sharing the same state name does not
permit a cross-machine transition: for example, proposal `APPROVED` cannot
transition directly to job `READY_TO_SUBMIT`.

## Concurrency, retries, and audit

A command supplies the expected state and an idempotency key. A mismatched
persisted state is `state_conflict`; an unlisted edge is `invalid_transition`;
mixing state types is `cross_machine_transition`. Replaying the same command/key
returns the original result and adds no audit event. Reusing a key for a
different command is `idempotency_conflict`.

On success, the repository stages the new state and one `state_transition` audit
event in the same UoW. The event records UUID identifiers, old/new state, actor,
reason, correlation ID, idempotency key, and UTC time. No state write or audit
write may survive alone.
