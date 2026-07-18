from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
import json
import re
from typing import Self
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from pydantic import field_validator, model_validator


class PolicyMode(StrEnum):
    disabled = "disabled"
    manual_only = "manual_only"
    public_feed = "public_feed"
    official_api_read = "official_api_read"
    official_api_write_with_confirmation = "official_api_write_with_confirmation"
    internal_test_fixture = "internal_test_fixture"


class PolicyAction(StrEnum):
    discover = "discover"
    read_detail = "read_detail"
    store = "store"
    notify = "notify"
    draft = "draft"
    open_link = "open_link"
    submit = "submit"
    message = "message"
    follow_up = "follow_up"


NETWORK_ACTIONS: frozenset[PolicyAction] = frozenset(
    {PolicyAction.discover, PolicyAction.read_detail}
)
WRITE_ACTIONS: frozenset[PolicyAction] = frozenset(
    {PolicyAction.submit, PolicyAction.message, PolicyAction.follow_up}
)
NETWORK_MODES: frozenset[PolicyMode] = frozenset(
    {PolicyMode.public_feed, PolicyMode.official_api_read}
)


class StrictPolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=False)


class PlatformLimits(StrictPolicyModel):
    requests_per_minute: StrictInt = Field(ge=0)
    retention_days: StrictInt = Field(ge=1)


class PlatformPolicy(StrictPolicyModel):
    platform_id: StrictStr = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    display_name: StrictStr = Field(min_length=1)
    reviewed_at: date
    review_due_at: date
    terms_url: StrictStr = Field(min_length=1)
    help_or_api_url: StrictStr = Field(min_length=1)
    owner_approved: StrictBool
    actions: dict[PolicyAction, PolicyMode]
    limits: PlatformLimits
    notes: StrictStr

    @field_validator("reviewed_at", "review_due_at", mode="before")
    @classmethod
    def validate_iso_date(cls, value: object) -> object:
        if isinstance(value, datetime):
            raise ValueError("policy dates must not include a time")
        if isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("policy dates must use YYYY-MM-DD")
        return value

    @field_validator("terms_url", "help_or_api_url")
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("policy references must be absolute HTTP(S) URLs")
        if parsed.username or parsed.password:
            raise ValueError("policy references must not contain credentials")
        return value

    @model_validator(mode="after")
    def validate_policy_authority(self) -> Self:
        expected_actions = set(PolicyAction)
        actual_actions = set(self.actions)
        if actual_actions != expected_actions:
            missing = sorted(action.value for action in expected_actions - actual_actions)
            extra = sorted(str(action) for action in actual_actions - expected_actions)
            detail = ", ".join([*(f"missing {item}" for item in missing), *extra])
            raise ValueError(f"actions must contain exactly all policy actions: {detail}")
        if self.review_due_at < self.reviewed_at:
            raise ValueError("review_due_at must not precede reviewed_at")

        for action, mode in self.actions.items():
            if mode in NETWORK_MODES and action not in NETWORK_ACTIONS:
                raise ValueError(f"{action.value} cannot use read-only mode {mode.value}")
            if action in WRITE_ACTIONS and mode == PolicyMode.internal_test_fixture:
                raise ValueError(f"{action.value} cannot use fixture authority")
            if (
                action not in WRITE_ACTIONS
                and mode == PolicyMode.official_api_write_with_confirmation
            ):
                raise ValueError(f"{action.value} is not a write action")
            if mode in NETWORK_MODES | {PolicyMode.official_api_write_with_confirmation}:
                if not self.owner_approved:
                    raise ValueError(f"{action.value} network authority requires owner approval")
                if self.limits.requests_per_minute <= 0:
                    raise ValueError(f"{action.value} network authority requires a positive rate limit")
        return self


class PolicyRegistry(StrictPolicyModel):
    version: StrictStr = Field(min_length=1)
    platforms: list[PlatformPolicy] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_platforms(self) -> Self:
        platform_ids = [platform.platform_id for platform in self.platforms]
        duplicates = sorted(
            platform_id for platform_id in set(platform_ids) if platform_ids.count(platform_id) > 1
        )
        if duplicates:
            raise ValueError("duplicate platform_id values: " + ", ".join(duplicates))
        return self

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PolicyRegistry:
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")


class PolicyDecision(StrictPolicyModel):
    platform_id: str
    action: PolicyAction | str
    mode: PolicyMode | None
    allowed: bool
    reason: str
    reason_code: str
    policy_version: str
    action_id: str
    review_due_at: date | None = None

    def to_json(self) -> str:
        return self.model_dump_json()


class PolicyAuditEvent(StrictPolicyModel):
    event_type: str = "policy_decision"
    timestamp_utc: datetime
    action_id: str
    platform_id: str
    action: str
    mode: PolicyMode | None
    allowed: bool
    reason_code: str
    policy_version: str
    review_due_at: date | None
    network_requested: bool

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True)
