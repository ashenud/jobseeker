from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from job_agent.core.states import ApplicationState, require_transition


@dataclass(frozen=True)
class ApplicationEvent: from_state:ApplicationState; to_state:ApplicationState; reason:str; at:datetime=field(default_factory=lambda: datetime.now(UTC))
class ApplicationTimeline:
    def __init__(self)->None: self.state=ApplicationState.prepared; self.events:list[ApplicationEvent]=[]
    def transition(self,target:ApplicationState,reason:str)->None:
        require_transition(self.state,target); self.events.append(ApplicationEvent(self.state,target,reason)); self.state=target
def schedule_follow_up(submitted_at:datetime, days:int=5)->datetime: return submitted_at + timedelta(days=days)
def funnel_metrics(timelines:list[ApplicationTimeline])->dict[str,int]:
    return {state.value: sum(1 for t in timelines if t.state==state) for state in ApplicationState}
