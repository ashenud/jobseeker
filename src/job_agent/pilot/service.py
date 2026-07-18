from dataclasses import dataclass
from enum import StrEnum


class PilotPhase(StrEnum): shadow="shadow"; assisted="assisted"; stable="stable"
@dataclass(frozen=True)
class PilotConfig: phase:PilotPhase=PilotPhase.shadow; daily_application_limit:int=3; real_write_connectors_enabled:bool=False
def enforce(config:PilotConfig)->None:
    if config.real_write_connectors_enabled: raise RuntimeError("Real write connectors require separate post-pilot approval")
def daily_report(decisions:int, drafts:int, submissions:int)->dict[str,int|str]: return {"mode":"pilot","decisions":decisions,"drafts":drafts,"manual_submissions":submissions}
