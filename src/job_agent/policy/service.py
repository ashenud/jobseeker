from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import re
from typing import Callable

from pydantic import ValidationError
import yaml

from .exceptions import PolicyConfigurationError, PolicyDeniedError
from .models import (
    NETWORK_MODES,
    WRITE_ACTIONS,
    PolicyAction,
    PolicyAuditEvent,
    PolicyDecision,
    PolicyMode,
    PolicyRegistry,
)


Clock = Callable[[], datetime]
AuditSink = Callable[[PolicyAuditEvent], None]
MAX_CONFIRMATION_TTL_SECONDS = 300


def utc_now() -> datetime:
    return datetime.now(UTC)


def _safe_now(clock: Clock) -> datetime:
    now = clock()
    if now.tzinfo is None or now.utcoffset() is None:
        raise PolicyConfigurationError("policy clock must return a timezone-aware datetime")
    return now.astimezone(UTC)


@dataclass(frozen=True)
class RuntimeFlags:
    api_write_enabled: bool = False
    browser_fill_enabled: bool = False
    outreach_sending_enabled: bool = False
    confirmation_ttl_seconds: int = 300

    def __post_init__(self) -> None:
        if not 0 < self.confirmation_ttl_seconds <= MAX_CONFIRMATION_TTL_SECONDS:
            raise ValueError("confirmation_ttl_seconds must be between 1 and 300")


@dataclass
class ConfirmationRecord:
    token_hash: str
    platform_id: str
    action: PolicyAction
    destination: str
    checksum: str
    action_id: str
    expires_at: datetime
    used: bool = False


class ConfirmationTokenService:
    def __init__(
        self,
        *,
        clock: Clock = utc_now,
        max_ttl_seconds: int = MAX_CONFIRMATION_TTL_SECONDS,
    ) -> None:
        if not 0 < max_ttl_seconds <= MAX_CONFIRMATION_TTL_SECONDS:
            raise ValueError("max_ttl_seconds must be between 1 and 300")
        self._clock = clock
        self._max_ttl_seconds = max_ttl_seconds
        self._records: dict[str, ConfirmationRecord] = {}

    def issue(
        self,
        platform_id: str,
        action: PolicyAction,
        destination: str,
        checksum: str,
        ttl_seconds: int = 300,
        *,
        action_id: str = "",
    ) -> str:
        if action not in WRITE_ACTIONS:
            raise ValueError("confirmation tokens may bind only write actions")
        if (
            not platform_id
            or not destination
            or not checksum
            or not 0 < ttl_seconds <= self._max_ttl_seconds
        ):
            raise ValueError("confirmation bindings must be nonempty and TTL within the maximum")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._records[digest] = ConfirmationRecord(
            digest,
            platform_id,
            action,
            destination,
            checksum,
            action_id,
            _safe_now(self._clock) + timedelta(seconds=ttl_seconds),
        )
        return token

    def consume(
        self,
        token: str,
        platform_id: str,
        action: PolicyAction,
        destination: str,
        checksum: str,
        *,
        action_id: str = "",
    ) -> bool:
        record = self._records.get(hashlib.sha256(token.encode()).hexdigest())
        if record is None or record.used or record.expires_at <= _safe_now(self._clock):
            return False
        expected = (record.platform_id, record.action, record.destination, record.checksum)
        if expected != (platform_id, action, destination, checksum):
            return False
        if record.action_id and record.action_id != action_id:
            return False
        record.used = True
        return True


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise PolicyConfigurationError("policy mapping keys must be scalar") from exc
        if duplicate:
            raise PolicyConfigurationError(f"duplicate policy mapping key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


class PolicyService:
    def __init__(
        self,
        registry: PolicyRegistry,
        today: date | None = None,
        flags: RuntimeFlags | None = None,
        tokens: ConfirmationTokenService | None = None,
        *,
        clock: Clock = utc_now,
        audit_sink: AuditSink | None = None,
    ) -> None:
        self.registry = registry
        self._clock = clock
        self._today = today
        self.flags = flags or RuntimeFlags()
        self.tokens = tokens or ConfirmationTokenService(
            clock=clock,
            max_ttl_seconds=self.flags.confirmation_ttl_seconds,
        )
        self._by_id = {platform.platform_id: platform for platform in registry.platforms}
        self._audit_sink = audit_sink
        self._audit_events: list[PolicyAuditEvent] = []

    @property
    def audit_events(self) -> tuple[PolicyAuditEvent, ...]:
        return tuple(self._audit_events)

    @classmethod
    def from_yaml(
        cls,
        path: Path | str = "config/platform_policy.yaml",
        *,
        today: date | None = None,
        flags: RuntimeFlags | None = None,
        tokens: ConfirmationTokenService | None = None,
        clock: Clock = utc_now,
        audit_sink: AuditSink | None = None,
    ) -> PolicyService:
        try:
            raw = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
            registry = PolicyRegistry.model_validate(raw)
        except (OSError, yaml.YAMLError, ValidationError, TypeError) as exc:
            raise PolicyConfigurationError("policy registry validation failed") from exc
        return cls(
            registry,
            today=today,
            flags=flags,
            tokens=tokens,
            clock=clock,
            audit_sink=audit_sink,
        )

    def _decision(
        self,
        platform_id: str,
        action: PolicyAction | str,
        mode: PolicyMode | None,
        allowed: bool,
        reason_code: str,
        reason: str,
        action_id: str,
        review_due_at: date | None,
        network: bool,
    ) -> PolicyDecision:
        decision = PolicyDecision(
            platform_id=platform_id,
            action=action,
            mode=mode,
            allowed=allowed,
            reason=reason,
            reason_code=reason_code,
            policy_version=self.registry.version,
            action_id=action_id,
            review_due_at=review_due_at,
        )
        event = PolicyAuditEvent(
            timestamp_utc=_safe_now(self._clock),
            action_id=action_id,
            platform_id=platform_id,
            action=action.value if isinstance(action, PolicyAction) else action,
            mode=mode,
            allowed=allowed,
            reason_code=reason_code,
            policy_version=self.registry.version,
            review_due_at=review_due_at,
            network_requested=network,
        )
        self._audit_events.append(event)
        if self._audit_sink is not None:
            self._audit_sink(event)
        return decision

    def decide(
        self,
        platform_id: str,
        action: PolicyAction | str,
        network: bool = False,
        confirmation_token: str | None = None,
        destination: str = "",
        checksum: str = "",
        *,
        action_id: str | None = None,
    ) -> PolicyDecision:
        safe_action_id = action_id or f"policy-{secrets.token_hex(12)}"
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", safe_action_id):
            safe_action_id = f"policy-{secrets.token_hex(12)}"
        try:
            policy_action = action if isinstance(action, PolicyAction) else PolicyAction(action)
        except ValueError:
            return self._decision(
                platform_id,
                action,
                None,
                False,
                "unknown_action",
                "Unknown action denied",
                safe_action_id,
                None,
                network,
            )
        platform = self._by_id.get(platform_id)
        if platform is None:
            return self._decision(
                platform_id,
                policy_action,
                None,
                False,
                "unknown_platform",
                "Unknown platform denied",
                safe_action_id,
                None,
                network,
            )
        mode = platform.actions[policy_action]
        current_date = self._today or _safe_now(self._clock).date()
        external = network or mode in NETWORK_MODES or policy_action in WRITE_ACTIONS
        if external and current_date < platform.reviewed_at:
            code, reason = "policy_not_yet_valid", "Policy review is not yet valid"
        elif external and current_date > platform.review_due_at:
            code, reason = "policy_expired", "Policy review expired"
        elif mode == PolicyMode.disabled:
            code, reason = "disabled", "Policy mode is disabled"
        elif mode == PolicyMode.manual_only and network:
            code, reason = "manual_network_denied", "Manual-only policy denies network I/O"
        elif mode == PolicyMode.manual_only and policy_action in WRITE_ACTIONS:
            code, reason = "manual_write_denied", "Manual-only write requires owner action"
        elif mode == PolicyMode.internal_test_fixture and (
            network or policy_action in WRITE_ACTIONS
        ):
            code, reason = "fixture_external_denied", "Test fixtures cannot authorize external I/O"
        elif mode == PolicyMode.official_api_write_with_confirmation:
            enabled = (
                self.flags.api_write_enabled
                if policy_action == PolicyAction.submit
                else self.flags.outreach_sending_enabled
            )
            if not enabled:
                code, reason = "runtime_write_disabled", "Runtime write feature is disabled"
            elif confirmation_token is None:
                code, reason = "confirmation_required", "Single-use confirmation is required"
            elif not self.tokens.consume(
                confirmation_token,
                platform_id,
                policy_action,
                destination,
                checksum,
                action_id=action_id or "",
            ):
                code, reason = "confirmation_invalid", "Confirmation is invalid or expired"
            else:
                return self._decision(
                    platform_id,
                    policy_action,
                    mode,
                    True,
                    "allowed",
                    "Allowed by current policy",
                    safe_action_id,
                    platform.review_due_at,
                    network,
                )
        else:
            return self._decision(
                platform_id,
                policy_action,
                mode,
                True,
                "allowed",
                "Allowed by current policy",
                safe_action_id,
                platform.review_due_at,
                network,
            )
        return self._decision(
            platform_id,
            policy_action,
            mode,
            False,
            code,
            reason,
            safe_action_id,
            platform.review_due_at,
            network,
        )

    def require(
        self,
        platform_id: str,
        action: PolicyAction | str,
        network: bool = False,
        confirmation_token: str | None = None,
        destination: str = "",
        checksum: str = "",
        *,
        action_id: str | None = None,
    ) -> PolicyDecision:
        decision = self.decide(
            platform_id,
            action,
            network=network,
            confirmation_token=confirmation_token,
            destination=destination,
            checksum=checksum,
            action_id=action_id,
        )
        if not decision.allowed:
            raise PolicyDeniedError(decision)
        return decision
