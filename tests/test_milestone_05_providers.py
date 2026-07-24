from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from job_agent.providers.contracts import (
    ConfirmationToken,
    EmbeddingProvider,
    EvidenceRetriever,
    LLMProvider,
    NotificationProvider,
    PolicyDecision,
    SourceAdapter,
    SubmissionConnector,
    SubmissionRequest,
)

NOW = datetime(2026, 7, 25, 11, 0, tzinfo=UTC)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000000511")


def valid_submission_request(**overrides: object) -> SubmissionRequest:
    values: dict[str, object] = {
        "application_id": APPLICATION_ID,
        "correlation_id": UUID("00000000-0000-0000-0000-000000000512"),
        "destination": "destination-reference",
        "proposal_checksum": "sha256:proposal",
        "action": "submit",
        "policy": PolicyDecision(
            decision_id=UUID("00000000-0000-0000-0000-000000000513"),
            action="submit",
            destination="destination-reference",
            allowed=True,
            current=True,
            decided_at=NOW,
        ),
        "owner_feature_enabled": True,
        "confirmation": ConfirmationToken(
            token_id=UUID("00000000-0000-0000-0000-000000000514"),
            application_id=APPLICATION_ID,
            destination="destination-reference",
            proposal_checksum="sha256:proposal",
            action="submit",
            actor="owner",
            issued_at=NOW - timedelta(minutes=1),
            expires_at=NOW + timedelta(minutes=4),
            nonce_hash="sha256:nonce",
        ),
        "requested_at": NOW,
        "maximum_confirmation_lifetime": timedelta(minutes=5),
    }
    values.update(overrides)
    return SubmissionRequest(**values)  # type: ignore[arg-type]


def test_all_provider_protocol_operations_are_async() -> None:
    protocols = (
        SourceAdapter,
        LLMProvider,
        EmbeddingProvider,
        EvidenceRetriever,
        NotificationProvider,
        SubmissionConnector,
    )
    for protocol in protocols:
        operations = [
            member
            for name, member in inspect.getmembers(protocol, inspect.isfunction)
            if not name.startswith("_")
        ]
        assert operations
        assert all(inspect.iscoroutinefunction(operation) for operation in operations)


@pytest.mark.parametrize(
    "overrides",
    [
        {
            "policy": PolicyDecision(
                UUID("00000000-0000-0000-0000-000000000515"),
                "submit",
                "destination-reference",
                False,
                True,
                NOW,
            )
        },
        {
            "policy": PolicyDecision(
                UUID("00000000-0000-0000-0000-000000000516"),
                "submit",
                "destination-reference",
                True,
                False,
                NOW,
            )
        },
        {"owner_feature_enabled": False},
    ],
)
def test_submission_fails_closed_without_current_policy_and_owner_flag(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        valid_submission_request(**overrides)


def test_confirmation_is_bound_to_destination_checksum_action_and_application() -> None:
    unbound = ConfirmationToken(
        token_id=UUID("00000000-0000-0000-0000-000000000517"),
        application_id=APPLICATION_ID,
        destination="other-destination",
        proposal_checksum="sha256:proposal",
        action="submit",
        actor="owner",
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=4),
        nonce_hash="sha256:nonce",
    )
    with pytest.raises(ValueError, match="exact write"):
        valid_submission_request(confirmation=unbound)


@pytest.mark.parametrize(
    "used_at, issued_at, expires_at",
    [
        (NOW - timedelta(seconds=1), NOW - timedelta(minutes=1), NOW + timedelta(minutes=1)),
        (None, NOW + timedelta(seconds=1), NOW + timedelta(minutes=1)),
        (None, NOW - timedelta(minutes=2), NOW),
    ],
)
def test_confirmation_must_be_short_lived_current_and_single_use(
    used_at: datetime | None, issued_at: datetime, expires_at: datetime
) -> None:
    unusable = ConfirmationToken(
        token_id=UUID("00000000-0000-0000-0000-000000000518"),
        application_id=APPLICATION_ID,
        destination="destination-reference",
        proposal_checksum="sha256:proposal",
        action="submit",
        actor="owner",
        issued_at=issued_at,
        expires_at=expires_at,
        nonce_hash="sha256:nonce",
        used_at=used_at,
    )
    with pytest.raises(ValueError, match="expired, premature, or already used"):
        valid_submission_request(confirmation=unusable)


def test_valid_exactly_bound_submission_authorization_is_constructible() -> None:
    request = valid_submission_request()
    assert request.confirmation.is_usable_at(NOW)


def test_confirmation_lifetime_is_bounded_by_configuration() -> None:
    long_lived = ConfirmationToken(
        token_id=UUID("00000000-0000-0000-0000-000000000519"),
        application_id=APPLICATION_ID,
        destination="destination-reference",
        proposal_checksum="sha256:proposal",
        action="submit",
        actor="owner",
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(hours=1),
        nonce_hash="sha256:nonce",
    )
    with pytest.raises(ValueError, match="configured short lifetime"):
        valid_submission_request(confirmation=long_lived)
