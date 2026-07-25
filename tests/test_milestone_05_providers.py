from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta, timezone
import inspect
from typing import Any, Callable
from uuid import UUID

import pytest
from pydantic import ValidationError

from job_agent.policy.exceptions import PolicyDeniedError
from job_agent.policy.models import (
    AuthorizedExternalWrite,
    PolicyAction,
    PolicyDecision,
    PolicyRegistry,
)
from job_agent.policy.service import PolicyService, RuntimeFlags
from job_agent.providers.contracts import (
    DetailRequest,
    DiscoveryRequest,
    EmbeddingProvider,
    EmbeddingRequest,
    EvidenceRequest,
    EvidenceRetriever,
    LLMProvider,
    NotificationProvider,
    NotificationRequest,
    ProposalRequest,
    RawJob,
    ScoreRequest,
    SourceAdapter,
    SubmissionConnector,
    SubmissionReceipt,
    SubmissionRequest,
)

NOW = datetime(2026, 7, 25, 11, 0, tzinfo=UTC)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000000511")
CORRELATION_ID = UUID("00000000-0000-0000-0000-000000000512")
ACTION_ID = UUID("00000000-0000-0000-0000-000000000513")
REFERENCE = "synthetic_provider"
NON_UTC = timezone(timedelta(hours=5, minutes=30))


def policy_service(
    action: PolicyAction,
    *,
    write_enabled: bool = False,
) -> PolicyService:
    actions = {item.value: "disabled" for item in PolicyAction}
    actions[action.value] = (
        "official_api_write_with_confirmation"
        if action is PolicyAction.submit
        else "official_api_read"
    )
    data: dict[str, Any] = {
        "version": "m05-test-v1",
        "platforms": [
            {
                "platform_id": REFERENCE,
                "display_name": "Synthetic provider",
                "reviewed_at": "2026-07-01",
                "review_due_at": "2026-10-01",
                "terms_url": "https://example.test/terms",
                "help_or_api_url": "https://example.test/api",
                "owner_approved": True,
                "actions": actions,
                "limits": {"requests_per_minute": 2, "retention_days": 30},
                "notes": "Deterministic provider-contract test.",
            }
        ],
    }
    return PolicyService(
        PolicyRegistry.model_validate(data),
        today=date(2026, 7, 25),
        flags=RuntimeFlags(api_write_enabled=write_enabled),
        clock=lambda: NOW,
    )


def decision(action: PolicyAction) -> PolicyDecision:
    return policy_service(action).require(
        REFERENCE,
        action,
        network=True,
        action_id=f"{action.value}-0501",
    )


def read_request_factories() -> tuple[
    tuple[PolicyAction, Callable[[PolicyDecision], object]], ...
]:
    return (
        (
            PolicyAction.discover,
            lambda policy: DiscoveryRequest(
                ACTION_ID, CORRELATION_ID, REFERENCE, policy, NOW, None, 20
            ),
        ),
        (
            PolicyAction.read_detail,
            lambda policy: DetailRequest(
                ACTION_ID, CORRELATION_ID, REFERENCE, policy, NOW, "external-1"
            ),
        ),
        (
            PolicyAction.score,
            lambda policy: ScoreRequest(
                APPLICATION_ID,
                CORRELATION_ID,
                REFERENCE,
                policy,
                NOW,
                "schema-v1",
                "prompt-v1",
                {},
            ),
        ),
        (
            PolicyAction.draft,
            lambda policy: ProposalRequest(
                APPLICATION_ID,
                ACTION_ID,
                CORRELATION_ID,
                REFERENCE,
                policy,
                NOW,
                "schema-v1",
                "prompt-v1",
                {},
                (),
            ),
        ),
        (
            PolicyAction.embed,
            lambda policy: EmbeddingRequest(
                CORRELATION_ID, REFERENCE, policy, NOW, ("text",), "embed-v1"
            ),
        ),
        (
            PolicyAction.retrieve,
            lambda policy: EvidenceRequest(
                APPLICATION_ID,
                CORRELATION_ID,
                REFERENCE,
                policy,
                NOW,
                "packaging",
                5,
                "evidence-v1",
            ),
        ),
        (
            PolicyAction.notify,
            lambda policy: NotificationRequest(
                ACTION_ID,
                CORRELATION_ID,
                REFERENCE,
                policy,
                NOW,
                "recipient-0501",
                "review-ready",
                "v1",
                {},
            ),
        ),
    )


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


@pytest.mark.parametrize(("action", "factory"), read_request_factories())
def test_every_external_read_contract_accepts_exact_authoritative_policy(
    action: PolicyAction,
    factory: Callable[[PolicyDecision], object],
) -> None:
    request = factory(decision(action))
    assert request is not None


@pytest.mark.parametrize(("action", "factory"), read_request_factories())
def test_every_external_read_contract_requires_utc(
    action: PolicyAction,
    factory: Callable[[PolicyDecision], object],
) -> None:
    request = factory(decision(action))
    with pytest.raises(ValueError, match="requested_at must be UTC"):
        replace(request, requested_at=NOW.astimezone(NON_UTC))


def test_discovery_limit_has_no_provider_contract_threshold() -> None:
    request = DiscoveryRequest(
        ACTION_ID,
        CORRELATION_ID,
        REFERENCE,
        decision(PolicyAction.discover),
        NOW,
        None,
        10_000,
    )
    assert request.limit == 10_000


@pytest.mark.parametrize(("action", "factory"), read_request_factories())
@pytest.mark.parametrize("failure", ("denied", "wrong_action", "stale", "manual"))
def test_every_external_read_contract_fails_closed(
    action: PolicyAction,
    factory: Callable[[PolicyDecision], object],
    failure: str,
) -> None:
    exact = decision(action)
    if failure == "denied":
        invalid = exact.model_copy(update={"allowed": False})
    elif failure == "wrong_action":
        invalid = exact.model_copy(update={"action": PolicyAction.store})
    elif failure == "stale":
        invalid = exact.model_copy(update={"review_due_at": date(2026, 7, 24)})
    else:
        invalid = exact.model_copy(update={"mode": "manual_only"})

    with pytest.raises(ValueError, match="current exact"):
        factory(invalid)


def test_write_authorization_is_consumed_once_before_connector_request() -> None:
    policy = policy_service(PolicyAction.submit, write_enabled=True)
    action_id = "submit-0501"
    destination = "https://example.test/jobs/1"
    checksum = "sha256:proposal"
    token = policy.tokens.issue(
        REFERENCE,
        PolicyAction.submit,
        destination,
        checksum,
        action_id=action_id,
    )

    authorization = policy.authorize_external_write(
        REFERENCE,
        PolicyAction.submit,
        confirmation_token=token,
        destination=destination,
        checksum=checksum,
        action_id=action_id,
    )
    request = SubmissionRequest(
        application_id=APPLICATION_ID,
        correlation_id=CORRELATION_ID,
        destination=destination,
        proposal_checksum=checksum,
        idempotency_key=action_id,
        authorization=authorization,
    )

    assert request.authorization.action_id == action_id
    with pytest.raises(PolicyDeniedError):
        policy.authorize_external_write(
            REFERENCE,
            PolicyAction.submit,
            confirmation_token=token,
            destination=destination,
            checksum=checksum,
            action_id=action_id,
        )


def test_connector_request_rejects_rebound_consumed_authorization() -> None:
    policy = policy_service(PolicyAction.submit, write_enabled=True)
    token = policy.tokens.issue(
        REFERENCE,
        PolicyAction.submit,
        "https://example.test/jobs/1",
        "sha256:proposal",
        action_id="submit-0502",
    )
    authorization = policy.authorize_external_write(
        REFERENCE,
        PolicyAction.submit,
        confirmation_token=token,
        destination="https://example.test/jobs/1",
        checksum="sha256:proposal",
        action_id="submit-0502",
    )

    with pytest.raises(ValueError, match="exact submission"):
        SubmissionRequest(
            application_id=APPLICATION_ID,
            correlation_id=CORRELATION_ID,
            destination="https://example.test/jobs/2",
            proposal_checksum="sha256:proposal",
            idempotency_key="submit-0502",
            authorization=authorization,
        )


def test_provider_capture_receipt_and_write_capability_require_utc() -> None:
    with pytest.raises(ValueError, match="captured_at must be UTC"):
        RawJob(
            REFERENCE,
            "external-1",
            NOW.astimezone(NON_UTC),
            {},
        )
    with pytest.raises(ValueError, match="submitted_at must be UTC"):
        SubmissionReceipt(
            "submit-0503",
            "external-receipt",
            NOW.astimezone(NON_UTC),
            "sha256:request",
        )
    with pytest.raises(ValidationError, match="authorized_at must be UTC"):
        AuthorizedExternalWrite(
            platform_id=REFERENCE,
            action=PolicyAction.submit,
            destination="https://example.test/jobs/1",
            checksum="sha256:proposal",
            action_id="submit-0503",
            policy_version="m05-test-v1",
            authorized_at=NOW.astimezone(NON_UTC),
        )
