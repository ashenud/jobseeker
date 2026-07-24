"""Typed, provider-neutral asynchronous integration protocols.

The contracts carry bounded request metadata but choose no marketplace, model,
endpoint, credential, or product threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Cursor:
    value: str


@dataclass(frozen=True, slots=True)
class RawJob:
    source_id: str
    external_id: str
    captured_at: datetime
    payload: dict[str, object]


@dataclass(frozen=True, slots=True)
class DiscoveryRequest:
    action_id: UUID
    correlation_id: UUID
    policy_decision_id: UUID
    cursor: Cursor | None
    limit: int


@dataclass(frozen=True, slots=True)
class DiscoveryBatch:
    jobs: tuple[RawJob, ...]
    next_cursor: Cursor | None
    exhausted: bool


@dataclass(frozen=True, slots=True)
class DetailRequest:
    action_id: UUID
    correlation_id: UUID
    policy_decision_id: UUID
    external_id: str


class SourceAdapter(Protocol):
    source_id: str

    async def discover(self, request: DiscoveryRequest) -> DiscoveryBatch: ...

    async def fetch_detail(self, request: DetailRequest) -> RawJob: ...


@dataclass(frozen=True, slots=True)
class ScoreRequest:
    job_id: UUID
    correlation_id: UUID
    schema_version: str
    prompt_version: str
    canonical_job: dict[str, object]


@dataclass(frozen=True, slots=True)
class ScoreResult:
    run_id: UUID
    structured_output: dict[str, object]
    provider_metadata: dict[str, str | int | float]


@dataclass(frozen=True, slots=True)
class ProposalRequest:
    job_id: UUID
    proposal_id: UUID
    correlation_id: UUID
    schema_version: str
    prompt_version: str
    canonical_job: dict[str, object]
    evidence: tuple[EvidenceChunk, ...]


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
    texts: tuple[str, ...]
    configuration_version: str


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    vectors: tuple[tuple[float, ...], ...]
    dimensions: int
    provider_metadata: dict[str, str | int | float]


class EmbeddingProvider(Protocol):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...


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
class EvidenceRequest:
    job_id: UUID
    correlation_id: UUID
    query: str
    limit: int
    evidence_set_version: str


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
    recipient_reference: str
    template_id: str
    template_version: str
    context: dict[str, str]


@dataclass(frozen=True, slots=True)
class NotificationResult:
    notification_id: UUID
    accepted: bool
    provider_reference: str | None


class NotificationProvider(Protocol):
    async def notify(self, request: NotificationRequest) -> NotificationResult: ...


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    decision_id: UUID
    action: str
    destination: str
    allowed: bool
    current: bool
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class ConfirmationToken:
    token_id: UUID
    application_id: UUID
    destination: str
    proposal_checksum: str
    action: str
    actor: str
    issued_at: datetime
    expires_at: datetime
    nonce_hash: str
    used_at: datetime | None = None

    def is_usable_at(self, now: datetime) -> bool:
        return (
            self.used_at is None
            and self.issued_at <= now
            and now < self.expires_at
        )


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
    action: str
    policy: PolicyDecision
    owner_feature_enabled: bool
    confirmation: ConfirmationToken
    requested_at: datetime
    maximum_confirmation_lifetime: timedelta

    def __post_init__(self) -> None:
        if not self.policy.allowed or not self.policy.current:
            raise ValueError("a current allow policy decision is required")
        if (
            self.policy.action != self.action
            or self.policy.destination != self.destination
        ):
            raise ValueError("policy decision is not bound to this action and destination")
        if not self.owner_feature_enabled:
            raise ValueError("the owner feature flag is disabled")
        if self.maximum_confirmation_lifetime <= timedelta(0):
            raise ValueError("maximum confirmation lifetime must be positive")
        token = self.confirmation
        if (
            token.application_id != self.application_id
            or token.destination != self.destination
            or token.proposal_checksum != self.proposal_checksum
            or token.action != self.action
        ):
            raise ValueError("confirmation token is not bound to this exact write")
        if not token.is_usable_at(self.requested_at):
            raise ValueError("confirmation token is expired, premature, or already used")
        if token.expires_at - token.issued_at > self.maximum_confirmation_lifetime:
            raise ValueError("confirmation token exceeds the configured short lifetime")


@dataclass(frozen=True, slots=True)
class SubmissionReceipt:
    action_id: UUID
    external_reference: str
    submitted_at: datetime
    request_checksum: str


class SubmissionConnector(Protocol):
    async def prepare(self, request: SubmissionPreviewRequest) -> SubmissionPreview: ...

    async def submit(self, request: SubmissionRequest) -> SubmissionReceipt: ...
