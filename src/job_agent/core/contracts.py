"""Persistence boundaries for atomic aggregate transitions.

Concrete SQLAlchemy repositories and unit-of-work implementations belong to
Milestone 06.  Test doubles implementing these protocols live in tests only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Self
from uuid import UUID

from job_agent.core.audit import AuditEvent
from job_agent.core.commands import TransitionCommand
from job_agent.core.states import MachineName, MachineState


@dataclass(frozen=True, slots=True)
class TransitionResult:
    aggregate_type: MachineName
    aggregate_id: UUID
    previous_state: MachineState
    current_state: MachineState
    audit_event_id: UUID
    occurred_at: datetime
    command_fingerprint: str
    replayed: bool = False


class TransitionRepository(Protocol):
    def current_state(
        self, aggregate_type: MachineName, aggregate_id: UUID
    ) -> MachineState | None: ...

    def find_by_idempotency_key(
        self, aggregate_type: MachineName, idempotency_key: str
    ) -> TransitionResult | None: ...

    def stage_state_and_audit(
        self,
        command: TransitionCommand,
        event: AuditEvent,
        result: TransitionResult,
    ) -> None:
        """Stage one state update and its audit event as one persistence operation."""
        ...


class UnitOfWork(Protocol):
    transitions: TransitionRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> UnitOfWork: ...
