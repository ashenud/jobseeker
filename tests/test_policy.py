from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError
import pytest

from job_agent.policy.exceptions import PolicyConfigurationError, PolicyDeniedError
from job_agent.policy.models import PolicyAction, PolicyRegistry
from job_agent.policy.service import ConfirmationTokenService, PolicyService, RuntimeFlags
from job_agent.sources.adapters import FixtureFeedAdapter
from job_agent.submission.service import SubmissionPackage, build_package


ALL_ACTIONS = {action.value: "disabled" for action in PolicyAction}


def registry_data(
    *,
    actions: dict[str, str] | None = None,
    owner_approved: bool = False,
    requests_per_minute: int = 0,
) -> dict[str, Any]:
    return {
        "version": "test-1",
        "platforms": [
            {
                "platform_id": "synthetic",
                "display_name": "Synthetic",
                "reviewed_at": "2026-07-01",
                "review_due_at": "2026-10-01",
                "terms_url": "https://example.test/terms",
                "help_or_api_url": "https://example.test/api",
                "owner_approved": owner_approved,
                "actions": {**ALL_ACTIONS, **(actions or {})},
                "limits": {
                    "requests_per_minute": requests_per_minute,
                    "retention_days": 30,
                },
                "notes": "Synthetic registry for deterministic tests.",
            }
        ],
    }


def service(data: dict[str, Any] | None = None, **kwargs: Any) -> PolicyService:
    return PolicyService(
        PolicyRegistry.model_validate(data or registry_data()),
        today=date(2026, 7, 19),
        **kwargs,
    )


@pytest.mark.parametrize(
    "path", ["config/platform_policy.yaml", "config/platform_policy.example.yaml"]
)
def test_canonical_and_example_registries_are_strictly_valid(path: str) -> None:
    loaded = PolicyService.from_yaml(path, today=date(2026, 7, 19))
    assert loaded.registry.version
    assert all(set(platform.actions) == set(PolicyAction) for platform in loaded.registry.platforms)


def test_canonical_registry_grants_no_live_or_automated_write_authority() -> None:
    registry = PolicyService.from_yaml(today=date(2026, 7, 19)).registry
    forbidden = {
        "public_feed",
        "official_api_read",
        "official_api_write_with_confirmation",
        "internal_test_fixture",
    }
    assert not {
        mode.value
        for platform in registry.platforms
        for mode in platform.actions.values()
    } & forbidden


@pytest.mark.parametrize(
    "mutation",
    (
        lambda data: data.update(extra="forbidden"),
        lambda data: data["platforms"][0].update(extra="forbidden"),
        lambda data: data["platforms"][0]["limits"].update(extra=1),
        lambda data: data["platforms"][0]["actions"].pop("notify"),
        lambda data: data["platforms"][0]["limits"].update(requests_per_minute=-1),
        lambda data: data["platforms"][0]["limits"].update(retention_days=0),
        lambda data: data["platforms"][0].update(review_due_at="2026-06-01"),
    ),
)
def test_schema_rejects_extra_missing_date_and_limit_errors(mutation: Any) -> None:
    data = registry_data()
    mutation(data)
    with pytest.raises(ValidationError):
        PolicyRegistry.model_validate(data)


def test_schema_rejects_duplicate_platform_ids() -> None:
    data = registry_data()
    data["platforms"].append(dict(data["platforms"][0]))
    with pytest.raises(ValidationError, match="duplicate platform_id"):
        PolicyRegistry.model_validate(data)


@pytest.mark.parametrize(
    "data",
    (
        registry_data(actions={"discover": "public_feed"}, requests_per_minute=2),
        registry_data(
            actions={"submit": "official_api_write_with_confirmation"},
            requests_per_minute=2,
        ),
        registry_data(
            actions={"submit": "official_api_read"},
            owner_approved=True,
            requests_per_minute=2,
        ),
        registry_data(
            actions={"discover": "official_api_write_with_confirmation"},
            owner_approved=True,
            requests_per_minute=2,
        ),
        registry_data(
            actions={"store": "public_feed"},
            owner_approved=True,
            requests_per_minute=2,
        ),
        registry_data(actions={"submit": "internal_test_fixture"}),
    ),
)
def test_schema_rejects_authority_contradictions(data: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        PolicyRegistry.model_validate(data)


def test_yaml_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text("version: one\nversion: two\nplatforms: []\n", encoding="utf-8")
    with pytest.raises(PolicyConfigurationError, match="duplicate policy mapping key"):
        PolicyService.from_yaml(path)


def test_unknown_expired_disabled_and_manual_network_fail_closed() -> None:
    manual = service(registry_data(actions={"discover": "manual_only"}))
    assert manual.decide("missing", "discover", network=True).reason_code == "unknown_platform"
    assert manual.decide("synthetic", "missing", network=True).reason_code == "unknown_action"
    assert manual.decide("synthetic", "submit", network=True).reason_code == "disabled"
    assert (
        manual.decide("synthetic", "discover", network=True).reason_code
        == "manual_network_denied"
    )
    expired = PolicyService(manual.registry, today=date(2027, 1, 1))
    assert expired.decide("synthetic", "discover", network=True).reason_code == "policy_expired"


def test_denial_occurs_before_connector_io_and_synthetic_read_can_run() -> None:
    calls = 0

    def connector(policy: PolicyService) -> None:
        nonlocal calls
        policy.require("synthetic", "discover", network=True)
        calls += 1

    with pytest.raises(PolicyDeniedError):
        connector(service(registry_data(actions={"discover": "manual_only"})))
    assert calls == 0

    allowed = registry_data(
        actions={"discover": "public_feed"},
        owner_approved=True,
        requests_per_minute=2,
    )
    connector(service(allowed))
    assert calls == 1


def test_existing_connector_seams_remain_uncalled_after_policy_denial() -> None:
    denied_policy = service(registry_data(actions={"discover": "manual_only"}))
    source = FixtureFeedAdapter(
        "synthetic",
        denied_policy,
        [{"id": "1", "url": "https://example.test/1", "title": "t", "body": "b"}],
    )
    with pytest.raises(PolicyDeniedError):
        source.fetch()
    assert source.network_called is False

    class TestWriteConnector:
        def __init__(self, policy: PolicyService) -> None:
            self.policy = policy
            self.sent: list[str] = []

        def submit(
            self, package: SubmissionPackage, confirmation_token: str | None
        ) -> str:
            self.policy.require(
                package.platform_id,
                PolicyAction.submit,
                network=True,
                confirmation_token=confirmation_token,
                destination=package.destination_url,
                checksum=package.checksum,
            )
            self.sent.append(package.checksum)
            return "test-receipt"

    package = build_package("synthetic", "https://example.test/1", "proposal")
    writer = TestWriteConnector(denied_policy)
    with pytest.raises(PolicyDeniedError):
        writer.submit(package, None)
    assert writer.sent == []


class MutableClock:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 19, 12, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def test_confirmation_is_bound_single_use_and_expires() -> None:
    clock = MutableClock()
    tokens = ConfirmationTokenService(clock=clock)
    flags = RuntimeFlags(api_write_enabled=True, confirmation_ttl_seconds=30)
    data = registry_data(
        actions={"submit": "official_api_write_with_confirmation"},
        owner_approved=True,
        requests_per_minute=2,
    )
    policy = service(data, flags=flags, tokens=tokens, clock=clock)
    token = tokens.issue(
        "synthetic",
        PolicyAction.submit,
        "https://example.test/jobs/1",
        "checksum-1",
        flags.confirmation_ttl_seconds,
        action_id="action-1",
    )
    denied = policy.decide(
        "synthetic",
        "submit",
        network=True,
        confirmation_token=token,
        destination="https://example.test/jobs/2",
        checksum="checksum-1",
        action_id="action-1",
    )
    assert denied.reason_code == "confirmation_invalid"
    allowed = policy.require(
        "synthetic",
        "submit",
        network=True,
        confirmation_token=token,
        destination="https://example.test/jobs/1",
        checksum="checksum-1",
        action_id="action-1",
    )
    assert allowed.allowed
    assert (
        policy.decide(
            "synthetic",
            "submit",
            network=True,
            confirmation_token=token,
            destination="https://example.test/jobs/1",
            checksum="checksum-1",
            action_id="action-1",
        ).reason_code
        == "confirmation_invalid"
    )

    expiring = tokens.issue(
        "synthetic",
        PolicyAction.submit,
        "https://example.test/jobs/1",
        "checksum-2",
        5,
        action_id="action-2",
    )
    clock.now += timedelta(seconds=5)
    assert not tokens.consume(
        expiring,
        "synthetic",
        PolicyAction.submit,
        "https://example.test/jobs/1",
        "checksum-2",
        action_id="action-2",
    )


def test_confirmation_ttl_is_strictly_bounded() -> None:
    tokens = ConfirmationTokenService()
    with pytest.raises(ValueError, match="TTL"):
        tokens.issue(
            "synthetic",
            PolicyAction.submit,
            "https://example.test/jobs/1",
            "checksum",
            301,
        )
    with pytest.raises(ValueError, match="between 1 and 300"):
        RuntimeFlags(confirmation_ttl_seconds=301)


def test_confirmation_consume_is_atomic_under_concurrent_attempts() -> None:
    tokens = ConfirmationTokenService()
    token = tokens.issue(
        "synthetic",
        PolicyAction.submit,
        "https://example.test/jobs/1",
        "checksum",
        action_id="action-concurrent",
    )

    def consume() -> bool:
        return tokens.consume(
            token,
            "synthetic",
            PolicyAction.submit,
            "https://example.test/jobs/1",
            "checksum",
            action_id="action-concurrent",
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: consume(), range(32)))
    assert results.count(True) == 1


def test_read_authority_cannot_be_reused_for_write() -> None:
    read_only = service(
        registry_data(
            actions={"discover": "official_api_read"},
            owner_approved=True,
            requests_per_minute=2,
        ),
        flags=RuntimeFlags(api_write_enabled=True),
    )
    assert read_only.decide("synthetic", "discover", network=True).allowed
    assert not read_only.decide("synthetic", "submit", network=True).allowed


def test_audit_events_are_structured_and_secret_free() -> None:
    policy = service(registry_data(actions={"discover": "manual_only"}))
    secret = "never-log-this-token"
    decision = policy.decide(
        "synthetic",
        "discover",
        network=True,
        confirmation_token=secret,
        destination="https://private.example/secret",
        checksum="private-checksum",
        action_id="audit-1",
    )
    event = policy.audit_events[-1]
    payload = event.to_json()
    assert decision.reason_code == "manual_network_denied"
    assert json.loads(payload)["action_id"] == "audit-1"
    assert json.loads(payload)["policy_version"] == "test-1"
    assert secret not in payload
    assert "private.example" not in payload
    assert "private-checksum" not in payload
