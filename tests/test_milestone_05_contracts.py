from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from job_agent.core.audit import AuditEvent
from job_agent.core.commands import ExternalWriteProof, TransitionCommand
from job_agent.core.contracts import TransitionResult
from job_agent.core.errors import (
    AggregateNotFoundError,
    ExternalWriteProofRequiredError,
    IdempotencyConflictError,
    InvalidTransitionError,
    ProtectedTransitionError,
    StateConflictError,
    UnsafeAuditMetadataError,
)
from job_agent.core.states import (
    ApplicationState,
    JobState,
    MachineName,
    MachineState,
    ProposalState,
    machine_for_state,
)
from job_agent.core.transitions import ProposalApprovalService, TransitionApplicationService
from job_agent.workers.transitions import RetryableTransitionHandler

AGGREGATE_ID = UUID("00000000-0000-0000-0000-000000000501")
CORRELATION_ID = UUID("00000000-0000-0000-0000-000000000502")
EVENT_ID = UUID("00000000-0000-0000-0000-000000000503")
NOW = datetime(2026, 7, 25, 10, 30, tzinfo=UTC)


class FakeTransitionRepository:
    """Test-only model of the single atomic repository operation."""

    def __init__(self, state: MachineState) -> None:
        self.states = {(machine_for_state(state), AGGREGATE_ID): state}
        self.results: dict[tuple[MachineName, str], TransitionResult] = {}
        self.pending: tuple[TransitionCommand, AuditEvent, TransitionResult] | None = None
        self.audit_events: list[AuditEvent] = []

    def apply_transition(
        self,
        command: TransitionCommand,
        event: AuditEvent,
        result: TransitionResult,
    ) -> TransitionResult:
        previous = self.results.get(
            (command.aggregate_type, command.idempotency_key)
        )
        if previous is not None:
            if previous.command_fingerprint != result.command_fingerprint:
                raise IdempotencyConflictError(
                    machine=command.aggregate_type,
                    current_state=command.expected_state.value,
                    target_state=command.target_state.value,
                )
            return replace(previous, replayed=True)

        current = self.states.get((command.aggregate_type, command.aggregate_id))
        if current is None:
            raise AggregateNotFoundError(
                machine=command.aggregate_type,
                current_state=command.expected_state.value,
                target_state=command.target_state.value,
            )
        if current != command.expected_state:
            raise StateConflictError(
                machine=command.aggregate_type,
                current_state=command.expected_state.value,
                target_state=command.target_state.value,
                actual_state=current.value,
            )
        self.pending = (command, event, result)
        return result

    def commit_pending(self) -> None:
        if self.pending is None:
            return
        command, event, result = self.pending
        self.states[(command.aggregate_type, command.aggregate_id)] = result.current_state
        self.results[(command.aggregate_type, command.idempotency_key)] = result
        self.audit_events.append(event)
        self.pending = None


class FakeUnitOfWork:
    def __init__(self, repository: FakeTransitionRepository) -> None:
        self.transitions = repository
        self.commits = 0
        self.rollbacks = 0

    def __enter__(self) -> FakeUnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.transitions.commit_pending()
        self.commits += 1

    def rollback(self) -> None:
        self.transitions.pending = None
        self.rollbacks += 1


class FakeUnitOfWorkFactory:
    def __init__(self, repository: FakeTransitionRepository) -> None:
        self.repository = repository
        self.created: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        unit_of_work = FakeUnitOfWork(self.repository)
        self.created.append(unit_of_work)
        return unit_of_work


class TransitionAndSubmissionSpy:
    """Expose both ports so tests detect accidental submission calls."""

    def __init__(self, transitions: TransitionApplicationService) -> None:
        self._transitions = transitions
        self.executed: list[TransitionCommand] = []
        self.submission_calls: list[object] = []

    def execute(self, transition: TransitionCommand) -> TransitionResult:
        self.executed.append(transition)
        return self._transitions.execute(transition)

    def submit(self, request: object) -> None:
        self.submission_calls.append(request)
        raise AssertionError("approval and transition retries must not submit")


def command(
    *,
    expected_state: MachineState = JobState.DISCOVERED,
    target_state: MachineState = JobState.NORMALIZED,
    idempotency_key: str = "transition-0501",
    reason: str = "normalized_canonical_source_record",
    external_write_proof: ExternalWriteProof | None = None,
) -> TransitionCommand:
    return TransitionCommand(
        aggregate_type=machine_for_state(expected_state),
        aggregate_id=AGGREGATE_ID,
        expected_state=expected_state,
        target_state=target_state,
        actor="normalization-service",
        reason=reason,
        correlation_id=CORRELATION_ID,
        idempotency_key=idempotency_key,
        external_write_proof=external_write_proof,
    )


def service(
    repository: FakeTransitionRepository,
) -> tuple[TransitionApplicationService, FakeUnitOfWorkFactory]:
    factory = FakeUnitOfWorkFactory(repository)
    return (
        TransitionApplicationService(
            factory,
            clock=lambda: NOW,
            event_id_factory=lambda: EVENT_ID,
        ),
        factory,
    )


def test_transition_atomically_commits_state_and_secret_free_audit() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, factory = service(repository)

    result = transitions.execute(command())

    assert result.current_state is JobState.NORMALIZED
    assert repository.states[(MachineName.JOB, AGGREGATE_ID)] is JobState.NORMALIZED
    assert repository.audit_events == [
        AuditEvent(
            event_id=EVENT_ID,
            event_type="state_transition",
            aggregate_type=MachineName.JOB,
            aggregate_id=AGGREGATE_ID,
            from_state="DISCOVERED",
            to_state="NORMALIZED",
            actor="normalization-service",
            reason="normalized_canonical_source_record",
            correlation_id=CORRELATION_ID,
            idempotency_key="transition-0501",
            occurred_at=NOW,
        )
    ]
    assert factory.created[0].commits == 1


def test_expected_state_compare_and_swap_conflict_has_no_commit() -> None:
    repository = FakeTransitionRepository(JobState.NORMALIZED)
    transitions, factory = service(repository)

    with pytest.raises(StateConflictError) as caught:
        transitions.execute(command())

    assert caught.value.code == "state_conflict"
    assert caught.value.actual_state == "NORMALIZED"
    assert not repository.audit_events
    assert factory.created[0].commits == 0


def test_invalid_transition_fails_before_opening_transaction() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, factory = service(repository)

    with pytest.raises(InvalidTransitionError) as caught:
        transitions.execute(command(target_state=JobState.SCORED))

    assert caught.value.code == "invalid_transition"
    assert repository.pending is None
    assert factory.created == []


def test_duplicate_delivery_returns_original_result_without_second_audit() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    first_service, _ = service(repository)
    second_service, _ = service(repository)

    original = first_service.execute(command())
    replay = second_service.execute(command())

    assert replay.replayed is True
    assert replay.audit_event_id == original.audit_event_id
    assert len(repository.audit_events) == 1


def test_reusing_unique_idempotency_key_for_different_command_fails() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, _ = service(repository)
    transitions.execute(command())

    with pytest.raises(IdempotencyConflictError) as caught:
        transitions.execute(command(reason="different_operation"))

    assert caught.value.code == "idempotency_conflict"
    assert len(repository.audit_events) == 1


@pytest.mark.parametrize(
    "field_value",
    (
        "api_key=do-not-store",
        "bearer eyJhbGciOiJIUzI1NiJ9",
        "owner@example.test",
        "+94771234567",
        "eyJhbGciOiJIUzI1NiJ9.payload.signature",
        "free text reason",
    ),
)
def test_audit_metadata_rejects_secrets_pii_and_free_text(field_value: str) -> None:
    with pytest.raises(UnsafeAuditMetadataError):
        command(reason=field_value)


def test_proposal_approval_only_transitions_reviewed_revision() -> None:
    repository = FakeTransitionRepository(ProposalState.IN_REVIEW)
    transitions, _ = service(repository)
    boundary = TransitionAndSubmissionSpy(transitions)
    approval = ProposalApprovalService(boundary)

    result = approval.approve(
        command(
            expected_state=ProposalState.IN_REVIEW,
            target_state=ProposalState.APPROVED,
            idempotency_key="proposal-approval-0501",
            reason="owner_approved_reviewed_revision",
        )
    )

    assert result.current_state is ProposalState.APPROVED
    assert len(boundary.executed) == 1
    assert boundary.submission_calls == []


def test_submitted_api_requires_bound_connector_receipt() -> None:
    with pytest.raises(ExternalWriteProofRequiredError):
        command(
            expected_state=ApplicationState.PACKAGE_PREPARED,
            target_state=ApplicationState.SUBMITTED_API,
            idempotency_key="submit-api-0501",
            reason="connector_receipt_recorded",
        )


def test_retryable_worker_cannot_record_external_submission_even_with_receipt() -> None:
    proof = ExternalWriteProof(
        action_id="submit-api-0501",
        idempotency_key="submit-api-0501",
        destination_checksum="sha256:destination",
        receipt_reference="receipt-0501",
        completed_at=NOW,
    )
    protected = command(
        expected_state=ApplicationState.PACKAGE_PREPARED,
        target_state=ApplicationState.SUBMITTED_API,
        idempotency_key="submit-api-0501",
        reason="connector_receipt_recorded",
        external_write_proof=proof,
    )
    repository = FakeTransitionRepository(ApplicationState.PACKAGE_PREPARED)
    transitions, _ = service(repository)
    worker = RetryableTransitionHandler(transitions)

    with pytest.raises(ProtectedTransitionError):
        worker.handle(protected)
    assert not repository.audit_events


def test_retryable_worker_replays_local_transition_without_external_calls() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, _ = service(repository)
    boundary = TransitionAndSubmissionSpy(transitions)
    worker = RetryableTransitionHandler(boundary)

    first = worker.handle(command())
    retry = worker.handle(command())

    assert first.current_state is JobState.NORMALIZED
    assert retry.replayed is True
    assert len(boundary.executed) == 2
    assert len(repository.audit_events) == 1
    assert boundary.submission_calls == []
