"""Pure CRM read-model helpers.

Application state changes are owned exclusively by the core transition
application service; this module never mutates an aggregate or appends audit
events independently.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from job_agent.core.states import ApplicationState


def schedule_follow_up(submitted_at: datetime, days: int = 5) -> datetime:
    return submitted_at + timedelta(days=days)


def funnel_metrics(states: Iterable[ApplicationState]) -> dict[str, int]:
    snapshot = tuple(states)
    return {
        state.value: sum(1 for current in snapshot if current is state)
        for state in ApplicationState
    }
