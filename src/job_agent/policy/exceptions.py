from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import PolicyDecision


class PolicyError(Exception):
    """Base class for safe policy-layer failures."""


class PolicyConfigurationError(PolicyError, ValueError):
    """Raised when the policy registry cannot be validated safely."""


class PolicyDeniedError(PolicyError, PermissionError):
    """Raised before I/O when a platform/action is not authorized."""

    def __init__(self, decision: PolicyDecision):
        super().__init__(decision.reason)
        self.decision = decision
