from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

from .exceptions import PolicyDeniedError
from .models import (
    NETWORK_ACTIONS,
    WRITE_ACTIONS,
    PolicyAction,
    PolicyDecision,
    PolicyMode,
    PolicyRegistry,
)


@dataclass(frozen=True)
class RuntimeFlags:
    api_write_enabled: bool = False
    browser_fill_enabled: bool = False
    outreach_sending_enabled: bool = False
    confirmation_ttl_seconds: int = 300


@dataclass
class ConfirmationRecord:
    token_hash: str
    platform_id: str
    action: PolicyAction
    destination: str
    checksum: str
    expires_at: datetime
    used: bool = False


class ConfirmationTokenService:
    def __init__(self) -> None:
        self._records: dict[str, ConfirmationRecord] = {}

    def issue(
        self,
        platform_id: str,
        action: PolicyAction,
        destination: str,
        checksum: str,
        ttl_seconds: int = 300,
    ) -> str:
        token = secrets.token_urlsafe(24)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._records[digest] = ConfirmationRecord(
            digest,
            platform_id,
            action,
            destination,
            checksum,
            datetime.now(UTC) + timedelta(seconds=ttl_seconds),
        )
        return token

    def consume(
        self,
        token: str,
        platform_id: str,
        action: PolicyAction,
        destination: str,
        checksum: str,
    ) -> bool:
        record = self._records.get(hashlib.sha256(token.encode()).hexdigest())
        if not record or record.used or record.expires_at < datetime.now(UTC):
            return False
        if (
            record.platform_id,
            record.action,
            record.destination,
            record.checksum,
        ) != (platform_id, action, destination, checksum):
            return False
        record.used = True
        return True


class PolicyService:
    def __init__(
        self,
        registry: PolicyRegistry,
        today: date | None = None,
        flags: RuntimeFlags | None = None,
        tokens: ConfirmationTokenService | None = None,
    ):
        self.registry = registry
        self.today = today or date.today()
        self.flags = flags or RuntimeFlags()
        self.tokens = tokens or ConfirmationTokenService()
        self._by_id = {platform.platform_id: platform for platform in registry.platforms}

    @classmethod
    def from_yaml(
        cls,
        path: Path | str = "config/platform_policy.yaml",
        *,
        today: date | None = None,
        flags: RuntimeFlags | None = None,
        tokens: ConfirmationTokenService | None = None,
    ) -> PolicyService:
        try:
            raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError("policy registry is not valid YAML") from exc
        if not isinstance(raw, dict):
            raise ValueError("policy registry YAML root must be an object")
        data: dict[str, object] = {}
        for key, value in raw.items():
            if not isinstance(key, str):
                raise ValueError("policy registry YAML root keys must be strings")
            data[key] = value
        return cls(
            PolicyRegistry.from_dict(data),
            today=today,
            flags=flags,
            tokens=tokens,
        )

    def decide(
        self,
        platform_id: str,
        action: PolicyAction | str,
        network: bool = False,
        confirmation_token: str | None = None,
        destination: str = "",
        checksum: str = "",
    ) -> PolicyDecision:
        try:
            policy_action = action if isinstance(action, PolicyAction) else PolicyAction(action)
        except ValueError:
            return PolicyDecision(
                platform_id,
                action,
                None,
                False,
                "Unknown action denied",
                self.registry.version,
            )
        platform = self._by_id.get(platform_id)
        if not platform:
            return PolicyDecision(
                platform_id,
                policy_action,
                None,
                False,
                "Unknown platform denied",
                self.registry.version,
            )
        mode = platform.actions.get(policy_action)
        if mode is None:
            return PolicyDecision(
                platform_id,
                policy_action,
                None,
                False,
                "Unknown action denied",
                self.registry.version,
                platform.review_due_at,
            )
        if platform.review_due_at < self.today and (
            network
            or policy_action in NETWORK_ACTIONS
            or mode
            in {
                PolicyMode.public_feed,
                PolicyMode.official_api_read,
                PolicyMode.official_api_write_with_confirmation,
            }
        ):
            return PolicyDecision(
                platform_id,
                policy_action,
                mode,
                False,
                "Policy review expired",
                self.registry.version,
                platform.review_due_at,
            )
        allowed = (
            mode == PolicyMode.internal_test_fixture
            or (mode == PolicyMode.manual_only and not network and policy_action not in WRITE_ACTIONS)
            or (
                mode in {PolicyMode.public_feed, PolicyMode.official_api_read}
                and policy_action not in WRITE_ACTIONS
            )
        )
        if mode == PolicyMode.official_api_write_with_confirmation:
            allowed = False
            if self.flags.api_write_enabled and confirmation_token:
                allowed = self.tokens.consume(
                    confirmation_token,
                    platform_id,
                    policy_action,
                    destination,
                    checksum,
                )
        return PolicyDecision(
            platform_id,
            policy_action,
            mode,
            allowed,
            (
                "Allowed by current policy"
                if allowed
                else f"Mode {mode} does not permit requested operation"
            ),
            self.registry.version,
            platform.review_due_at,
        )

    def require(
        self,
        platform_id: str,
        action: PolicyAction | str,
        network: bool = False,
        confirmation_token: str | None = None,
        destination: str = "",
        checksum: str = "",
    ) -> PolicyDecision:
        decision = self.decide(
            platform_id,
            action,
            network=network,
            confirmation_token=confirmation_token,
            destination=destination,
            checksum=checksum,
        )
        if not decision.allowed:
            raise PolicyDeniedError(decision.reason)
        return decision
