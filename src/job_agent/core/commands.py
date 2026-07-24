"""Mutation commands accepted by the transition application service."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from uuid import UUID

from job_agent.core.audit import validate_audit_text
from job_agent.core.errors import CrossMachineTransitionError
from job_agent.core.states import MachineName, MachineState, machine_for_state


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
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
