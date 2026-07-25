"""Secret-free structured audit events."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from job_agent.core.errors import UnsafeAuditMetadataError
from job_agent.core.states import MachineName

_SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|authorization|bearer|cookie|password|secret)\s*[:=]"
)
_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")
_PHONE_PATTERN = re.compile(r"\+?[0-9][0-9() -]{7,}[0-9]")


def validate_audit_text(field_name: str, value: str, *, maximum_length: int) -> None:
    if not value or value != value.strip():
        raise UnsafeAuditMetadataError(f"{field_name} must be non-empty and trimmed")
    if len(value) > maximum_length:
        raise UnsafeAuditMetadataError(f"{field_name} exceeds {maximum_length} characters")
    if any(character in value for character in ("\n", "\r", "\0")):
        raise UnsafeAuditMetadataError(f"{field_name} must be single-line text")
    if _SECRET_PATTERN.search(value):
        raise UnsafeAuditMetadataError(f"{field_name} appears to contain secret material")
    if (
        not _SAFE_IDENTIFIER_PATTERN.fullmatch(value)
        or "@" in value
        or _PHONE_PATTERN.fullmatch(value)
        or value.count(".") > 1
    ):
        raise UnsafeAuditMetadataError(
            f"{field_name} must be a lowercase structured identifier, not free text or PII"
        )


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: UUID
    event_type: str
    aggregate_type: MachineName
    aggregate_id: UUID
    from_state: str
    to_state: str
    actor: str
    reason: str
    correlation_id: UUID
    idempotency_key: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.event_type != "state_transition":
            raise ValueError("event_type must be state_transition")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() != UTC.utcoffset(
            self.occurred_at
        ):
            raise ValueError("occurred_at must be UTC")
        validate_audit_text("actor", self.actor, maximum_length=120)
        validate_audit_text("reason", self.reason, maximum_length=500)
        validate_audit_text("idempotency_key", self.idempotency_key, maximum_length=200)
