"""Mutation commands accepted by the transition application service."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from job_agent.core.audit import validate_audit_text
from job_agent.core.errors import (
    CrossMachineTransitionError,
    ExternalWriteProofRequiredError,
)
from job_agent.core.states import (
    ApplicationState,
    JobState,
    MachineName,
    MachineState,
    machine_for_state,
)


@dataclass(frozen=True, slots=True)
class ExternalWriteProof:
    """Minimal immutable evidence that an authorized connector completed a write."""

    action_id: str
    idempotency_key: str
    destination_checksum: str
    receipt_reference: str
    completed_at: datetime

    def __post_init__(self) -> None:
        validate_audit_text("action_id", self.action_id, maximum_length=200)
        validate_audit_text("idempotency_key", self.idempotency_key, maximum_length=200)
        validate_audit_text(
            "destination_checksum", self.destination_checksum, maximum_length=200
        )
        validate_audit_text("receipt_reference", self.receipt_reference, maximum_length=200)
        if (
            self.completed_at.tzinfo is None
            or self.completed_at.utcoffset() != UTC.utcoffset(self.completed_at)
        ):
            raise ValueError("completed_at must be UTC")


@dataclass(frozen=True, slots=True)
class TransitionCommand:
    aggregate_type: MachineName
    aggregate_id: UUID
    expected_state: MachineState
    target_state: MachineState
    actor: str
    reason: str
    correlation_id: UUID
    idempotency_key: str
    external_write_proof: ExternalWriteProof | None = None

    def __post_init__(self) -> None:
        expected_machine = machine_for_state(self.expected_state)
        target_machine = machine_for_state(self.target_state)
        if expected_machine is not self.aggregate_type or target_machine is not self.aggregate_type:
            raise CrossMachineTransitionError(
                machine=self.aggregate_type,
                current_state=self.expected_state.value,
                target_state=self.target_state.value,
                target_machine=target_machine,
            )
        validate_audit_text("actor", self.actor, maximum_length=120)
        validate_audit_text("reason", self.reason, maximum_length=500)
        validate_audit_text("idempotency_key", self.idempotency_key, maximum_length=200)
        targets_external_submission = self.target_state in {
            JobState.SUBMITTED_API,
            ApplicationState.SUBMITTED_API,
        }
        if targets_external_submission:
            proof = self.external_write_proof
            if proof is None or proof.idempotency_key != self.idempotency_key:
                raise ExternalWriteProofRequiredError(
                    machine=self.aggregate_type,
                    current_state=self.expected_state.value,
                    target_state=self.target_state.value,
                )
        elif self.external_write_proof is not None:
            raise ValueError("external write proof is valid only for SUBMITTED_API")

    def fingerprint(self) -> str:
        canonical = json.dumps(
            {
                "aggregate_type": self.aggregate_type.value,
                "aggregate_id": str(self.aggregate_id),
                "expected_state": self.expected_state.value,
                "target_state": self.target_state.value,
                "actor": self.actor,
                "reason": self.reason,
                "correlation_id": str(self.correlation_id),
                "idempotency_key": self.idempotency_key,
                "external_write_proof": (
                    None
                    if self.external_write_proof is None
                    else {
                        "action_id": self.external_write_proof.action_id,
                        "idempotency_key": self.external_write_proof.idempotency_key,
                        "destination_checksum": (
                            self.external_write_proof.destination_checksum
                        ),
                        "receipt_reference": self.external_write_proof.receipt_reference,
                        "completed_at": self.external_write_proof.completed_at.isoformat(),
                    }
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
