"""Typed, provider-neutral asynchronous integration protocols.

Every request that may cross a process or network boundary carries the exact,
current policy decision produced by the authoritative policy service. External
writes instead carry a post-consumption capability: connectors never receive a
raw confirmation token or a caller-asserted feature flag.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from job_agent.policy.models import (
    AuthorizedExternalWrite,
    PolicyAction,
    PolicyDecision,
    PolicyMode,
)

_EXTERNAL_READ_MODES = {
    PolicyMode.public_feed,
    PolicyMode.official_api_read,
}


def _require_external_policy(
    policy: PolicyDecision,
    *,
    platform_id: str,
    action: PolicyAction,
    requested_at: datetime,
) -> None:
    """Fail closed unless a decision authorizes this exact external request."""
    _require_utc("requested_at", requested_at)
    if (
        not policy.allowed
        or policy.platform_id != platform_id
        or policy.action != action
        or policy.mode not in _EXTERNAL_READ_MODES
        or policy.review_due_at is None
        or requested_at.astimezone(UTC).date() > policy.review_due_at
    ):
        raise ValueError("a current exact external policy decision is required")


def _require_utc(field_name: str, value: datetime) -> None:
    if (
        value.tzinfo is None
        or value.utcoffset() != UTC.utcoffset(value)
    ):
        raise ValueError(f"{field_name} must be UTC")


@dataclass(frozen=True, slots=True)
class Cursor:
    value: str


@dataclass(frozen=True, slots=True)
class RawJob:
    source_id: str
    external_id: str
    captured_at: datetime
    payload: dict[str, object]

    def __post_init__(self) -> None:
        _require_utc("captured_at", self.captured_at)


@dataclass(frozen=True, slots=True)
class DiscoveryRequest:
    action_id: UUID
    correlation_id: UUID
    source_id: str
    policy: PolicyDecision
    requested_at: datetime
    cursor: Cursor | None
    limit: int

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.source_id,
            action=PolicyAction.discover,
            requested_at=self.requested_at,
        )
        if self.limit <= 0:
            raise ValueError("discovery limit must be positive")


@dataclass(frozen=True, slots=True)
class DiscoveryBatch:
    jobs: tuple[RawJob, ...]
    next_cursor: Cursor | None
    exhausted: bool


@dataclass(frozen=True, slots=True)
class DetailRequest:
    action_id: UUID
    correlation_id: UUID
    source_id: str
    policy: PolicyDecision
    requested_at: datetime
    external_id: str

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.source_id,
            action=PolicyAction.read_detail,
            requested_at=self.requested_at,
        )


class SourceAdapter(Protocol):
    source_id: str

    async def discover(self, request: DiscoveryRequest) -> DiscoveryBatch: ...

    async def fetch_detail(self, request: DetailRequest) -> RawJob: ...


@dataclass(frozen=True, slots=True)
class ScoreRequest:
    job_id: UUID
    correlation_id: UUID
    provider_reference: str
    policy: PolicyDecision
    requested_at: datetime
    schema_version: str
    prompt_version: str
    canonical_job: dict[str, object]

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.provider_reference,
            action=PolicyAction.score,
            requested_at=self.requested_at,
        )


@dataclass(frozen=True, slots=True)
class ScoreResult:
    run_id: UUID
    structured_output: dict[str, object]
    provider_metadata: dict[str, str | int | float]


@dataclass(frozen=True, slots=True)
class EvidenceChunk:
    chunk_id: UUID
    document_id: UUID
    title: str
    text: str
    content_hash: str
    verification_state: str
    restrictions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProposalRequest:
    job_id: UUID
    proposal_id: UUID
    correlation_id: UUID
    provider_reference: str
    policy: PolicyDecision
    requested_at: datetime
    schema_version: str
    prompt_version: str
    canonical_job: dict[str, object]
    evidence: tuple[EvidenceChunk, ...]

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.provider_reference,
            action=PolicyAction.draft,
            requested_at=self.requested_at,
        )


@dataclass(frozen=True, slots=True)
class ProposalResult:
    run_id: UUID
    body: str
    evidence_links: tuple[tuple[str, tuple[UUID, ...]], ...]
    structured_output: dict[str, object]
    provider_metadata: dict[str, str | int | float]


class LLMProvider(Protocol):
    async def score_job(self, request: ScoreRequest) -> ScoreResult: ...

    async def draft_proposal(self, request: ProposalRequest) -> ProposalResult: ...


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    correlation_id: UUID
    provider_reference: str
    policy: PolicyDecision
    requested_at: datetime
    texts: tuple[str, ...]
    configuration_version: str

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.provider_reference,
            action=PolicyAction.embed,
            requested_at=self.requested_at,
        )


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    vectors: tuple[tuple[float, ...], ...]
    dimensions: int
    provider_metadata: dict[str, str | int | float]


class EmbeddingProvider(Protocol):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...


@dataclass(frozen=True, slots=True)
class EvidenceRequest:
    job_id: UUID
    correlation_id: UUID
    store_reference: str
    policy: PolicyDecision
    requested_at: datetime
    query: str
    limit: int
    evidence_set_version: str

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.store_reference,
            action=PolicyAction.retrieve,
            requested_at=self.requested_at,
        )


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    chunks: tuple[EvidenceChunk, ...]
    evidence_set_version: str


class EvidenceRetriever(Protocol):
    async def retrieve(self, request: EvidenceRequest) -> EvidenceResult: ...


@dataclass(frozen=True, slots=True)
class NotificationRequest:
    notification_id: UUID
    correlation_id: UUID
    provider_reference: str
    policy: PolicyDecision
    requested_at: datetime
    recipient_reference: str
    template_id: str
    template_version: str
    context: dict[str, str]

    def __post_init__(self) -> None:
        _require_external_policy(
            self.policy,
            platform_id=self.provider_reference,
            action=PolicyAction.notify,
            requested_at=self.requested_at,
        )


@dataclass(frozen=True, slots=True)
class NotificationResult:
    notification_id: UUID
    accepted: bool
    provider_reference: str | None


class NotificationProvider(Protocol):
    async def notify(self, request: NotificationRequest) -> NotificationResult: ...


@dataclass(frozen=True, slots=True)
class SubmissionPreviewRequest:
    application_id: UUID
    correlation_id: UUID
    destination: str
    proposal_checksum: str


@dataclass(frozen=True, slots=True)
class SubmissionPreview:
    application_id: UUID
    destination: str
    proposal_checksum: str
    summary: str


@dataclass(frozen=True, slots=True)
class SubmissionRequest:
    application_id: UUID
    correlation_id: UUID
    destination: str
    proposal_checksum: str
    idempotency_key: str
    authorization: AuthorizedExternalWrite

    def __post_init__(self) -> None:
        authorization = self.authorization
        if (
            authorization.action is not PolicyAction.submit
            or authorization.destination != self.destination
            or authorization.checksum != self.proposal_checksum
            or authorization.action_id != self.idempotency_key
        ):
            raise ValueError("write authorization is not bound to this exact submission")


@dataclass(frozen=True, slots=True)
class SubmissionReceipt:
    action_id: str
    external_reference: str
    submitted_at: datetime
    request_checksum: str

    def __post_init__(self) -> None:
        _require_utc("submitted_at", self.submitted_at)


class SubmissionConnector(Protocol):
    async def prepare(self, request: SubmissionPreviewRequest) -> SubmissionPreview: ...

    async def submit(self, request: SubmissionRequest) -> SubmissionReceipt: ...
