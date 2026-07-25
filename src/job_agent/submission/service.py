"""Local submission-package and owner-reference helpers.

These functions produce immutable local evidence only. They do not mutate an
application state and they expose no production fake or network connector.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SubmissionPackage:
    platform_id: str
    destination_url: str
    proposal_body: str
    checksum: str
    status: str = "prepared"


def build_package(
    platform_id: str, destination_url: str, proposal_body: str
) -> SubmissionPackage:
    return SubmissionPackage(
        platform_id,
        destination_url,
        proposal_body,
        hashlib.sha256(proposal_body.encode()).hexdigest(),
    )


@dataclass(frozen=True, slots=True)
class ManualSubmissionReference:
    application_id: UUID
    reference: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        if not self.reference or self.reference != self.reference.strip():
            raise ValueError("reference is required and must be trimmed")
        if (
            self.recorded_at.tzinfo is None
            or self.recorded_at.utcoffset() != UTC.utcoffset(self.recorded_at)
        ):
            raise ValueError("recorded_at must be UTC")


def record_manual_submission_reference(
    application_id: UUID,
    reference: str,
    *,
    recorded_at: datetime,
) -> ManualSubmissionReference:
    """Record owner-supplied evidence without asserting a state transition."""
    return ManualSubmissionReference(application_id, reference, recorded_at)
