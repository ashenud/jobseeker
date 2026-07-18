from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


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


NETWORK_ACTIONS: set[PolicyAction] = {PolicyAction.discover, PolicyAction.read_detail}
WRITE_ACTIONS: set[PolicyAction] = {
    PolicyAction.submit,
    PolicyAction.message,
    PolicyAction.follow_up,
}


def _string_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{label} keys must be strings")
        result[key] = item
    return result


def _required_string(values: dict[str, object], key: str, label: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}.{key} must be a nonempty string")
    return value


def _required_integer(values: dict[str, object], key: str, label: str) -> int:
    value = values.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label}.{key} must be an integer")
    return value


def _required_date(values: dict[str, object], key: str, label: str) -> date:
    value = _required_string(values, key, label)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}.{key} must be an ISO date") from exc


@dataclass(frozen=True)
class PlatformLimits:
    requests_per_minute: int
    retention_days: int


@dataclass(frozen=True)
class PlatformPolicy:
    platform_id: str
    display_name: str
    reviewed_at: date
    review_due_at: date
    terms_url: str
    help_or_api_url: str | None
    owner_approved: bool
    actions: dict[PolicyAction, PolicyMode]
    limits: PlatformLimits
    notes: str = ""


@dataclass(frozen=True)
class PolicyRegistry:
    version: str
    platforms: list[PlatformPolicy]

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PolicyRegistry:
        version = _required_string(data, "version", "policy registry")
        raw_platforms = data.get("platforms")
        if not isinstance(raw_platforms, list):
            raise ValueError("policy registry.platforms must be a list")

        platforms: list[PlatformPolicy] = []
        for index, raw_platform in enumerate(raw_platforms):
            label = f"policy registry.platforms[{index}]"
            values = _string_mapping(raw_platform, label)
            platform_id = _required_string(values, "platform_id", label)

            raw_actions = _string_mapping(values.get("actions"), f"{label}.actions")
            actions: dict[PolicyAction, PolicyMode] = {}
            for action_name, mode_name in raw_actions.items():
                if not isinstance(mode_name, str):
                    raise ValueError(f"{label}.actions.{action_name} must be a string")
                try:
                    action = PolicyAction(action_name)
                    mode = PolicyMode(mode_name)
                except ValueError as exc:
                    raise ValueError(
                        f"{label}.actions contains an unknown action or mode"
                    ) from exc
                actions[action] = mode

            raw_limits = _string_mapping(values.get("limits"), f"{label}.limits")
            limits = PlatformLimits(
                requests_per_minute=_required_integer(
                    raw_limits, "requests_per_minute", f"{label}.limits"
                ),
                retention_days=_required_integer(
                    raw_limits, "retention_days", f"{label}.limits"
                ),
            )
            owner_approved = values.get("owner_approved")
            if not isinstance(owner_approved, bool):
                raise ValueError(f"{label}.owner_approved must be a boolean")
            help_or_api_url = values.get("help_or_api_url")
            if help_or_api_url is not None and not isinstance(help_or_api_url, str):
                raise ValueError(f"{label}.help_or_api_url must be a string or null")
            notes = values.get("notes", "")
            if not isinstance(notes, str):
                raise ValueError(f"{label}.notes must be a string")

            platform = PlatformPolicy(
                platform_id=platform_id,
                display_name=_required_string(values, "display_name", label),
                reviewed_at=_required_date(values, "reviewed_at", label),
                review_due_at=_required_date(values, "review_due_at", label),
                terms_url=_required_string(values, "terms_url", label),
                help_or_api_url=help_or_api_url,
                owner_approved=owner_approved,
                actions=actions,
                limits=limits,
                notes=notes,
            )
            for action, mode in actions.items():
                if (
                    action in WRITE_ACTIONS
                    and mode == PolicyMode.official_api_write_with_confirmation
                    and not platform.owner_approved
                ):
                    raise ValueError(
                        f"{platform.platform_id}:{action} write mode requires owner_approved"
                    )
                if (
                    mode in {PolicyMode.public_feed, PolicyMode.official_api_read}
                    and limits.requests_per_minute <= 0
                ):
                    raise ValueError(
                        f"{platform.platform_id}:{action} network mode needs positive rate limit"
                    )
            platforms.append(platform)
        return cls(version=version, platforms=platforms)

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "platforms": [
                {
                    "platform_id": platform.platform_id,
                    "display_name": platform.display_name,
                    "reviewed_at": platform.reviewed_at.isoformat(),
                    "review_due_at": platform.review_due_at.isoformat(),
                    "terms_url": platform.terms_url,
                    "help_or_api_url": platform.help_or_api_url,
                    "owner_approved": platform.owner_approved,
                    "actions": {
                        action.value: mode.value for action, mode in platform.actions.items()
                    },
                    "limits": {
                        "requests_per_minute": platform.limits.requests_per_minute,
                        "retention_days": platform.limits.retention_days,
                    },
                    "notes": platform.notes,
                }
                for platform in self.platforms
            ],
        }


@dataclass(frozen=True)
class PolicyDecision:
    platform_id: str
    action: PolicyAction | str
    mode: PolicyMode | None
    allowed: bool
    reason: str
    policy_version: str
    review_due_at: date | None = None

    def to_json(self) -> str:
        import json

        action = self.action.value if isinstance(self.action, PolicyAction) else self.action
        return json.dumps(
            {
                "platform_id": self.platform_id,
                "action": action,
                "mode": None if self.mode is None else self.mode.value,
                "allowed": self.allowed,
                "reason": self.reason,
                "policy_version": self.policy_version,
                "review_due_at": (
                    None if self.review_due_at is None else self.review_due_at.isoformat()
                ),
            }
        )
