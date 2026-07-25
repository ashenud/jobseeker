"""Stable typed errors for aggregate transitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from job_agent.core.states import MachineName


@dataclass(eq=False)
class TransitionError(ValueError):
    machine: MachineName
    current_state: str | None
    target_state: str | None

    code: ClassVar[str] = "transition_error"

    @property
    def message(self) -> str:
        return "The requested state transition could not be completed."

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "message": self.message,
            "machine": self.machine.value,
            "current_state": self.current_state,
            "target_state": self.target_state,
        }


@dataclass(eq=False)
class InvalidTransitionError(TransitionError):
    code: ClassVar[str] = "invalid_transition"

    @property
    def message(self) -> str:
        return (
            f"{self.machine.value} cannot transition from "
            f"{self.current_state} to {self.target_state}"
        )


@dataclass(eq=False)
class CrossMachineTransitionError(TransitionError):
    target_machine: MachineName
    code: ClassVar[str] = "cross_machine_transition"

    @property
    def message(self) -> str:
        return (
            f"a {self.machine.value} state cannot transition to a "
            f"{self.target_machine.value} state"
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            **super().to_dict(),
            "target_machine": self.target_machine.value,
        }


@dataclass(eq=False)
class StateConflictError(TransitionError):
    actual_state: str
    code: ClassVar[str] = "state_conflict"

    @property
    def message(self) -> str:
        return (
            f"expected {self.current_state}, but the aggregate is "
            f"currently {self.actual_state}"
        )


@dataclass(eq=False)
class AggregateNotFoundError(TransitionError):
    code: ClassVar[str] = "aggregate_not_found"

    @property
    def message(self) -> str:
        return f"{self.machine.value} aggregate was not found"


@dataclass(eq=False)
class IdempotencyConflictError(TransitionError):
    code: ClassVar[str] = "idempotency_conflict"

    @property
    def message(self) -> str:
        return "idempotency key was already used for a different transition"


@dataclass(eq=False)
class ExternalWriteProofRequiredError(TransitionError):
    code: ClassVar[str] = "external_write_proof_required"

    @property
    def message(self) -> str:
        return "SUBMITTED_API requires a bound connector receipt"


@dataclass(eq=False)
class ProtectedTransitionError(TransitionError):
    code: ClassVar[str] = "protected_transition"

    @property
    def message(self) -> str:
        return "retryable transition workers cannot record external submission"


class UnsafeAuditMetadataError(ValueError):
    """Raised before unsafe metadata can enter a structured audit event."""
